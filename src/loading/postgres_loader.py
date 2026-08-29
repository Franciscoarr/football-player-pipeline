import logging
import psycopg2
from psycopg2.extras import execute_batch
from src.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_teams(cursor, teams: list):
    """
    Inserta o actualiza los equipos de forma idempotente
    """
    if not teams:
        return

    query = """
        INSERT INTO teams (team_id, name, country)
        VALUES (%(team_id)s, %(name)s, %(country)s)
        ON CONFLICT (team_id) 
        DO UPDATE SET 
            name = EXCLUDED.name, 
            country = EXCLUDED.country;
    """
    execute_batch(cursor, query, teams)
    logging.info(f"Equipos procesados: {len(teams)}")

def load_players(cursor, players: list):
    """
    Inserta o actualiza los jugadores de forma idempotente
    """
    if not players:
        return

    query = """
        INSERT INTO players (player_id, name, firstname, lastname, age, nationality, height, weight)
        VALUES (%(player_id)s, %(name)s, %(firstname)s, %(lastname)s, %(age)s, %(nationality)s, %(height)s, %(weight)s)
        ON CONFLICT (player_id) 
        DO UPDATE SET 
            age = EXCLUDED.age,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight;
    """
    execute_batch(cursor, query, players)
    logging.info(f"Jugadores procesados: {len(players)}")

def load_statistics(cursor, statistics: list):
    """
    Inserta o actualiza las estadísticas de forma idempotente
    """
    if not statistics:
        return

    query = """
        INSERT INTO player_statistics (
            player_id, team_id, season, competition, appearances, starts, minutes, 
            goals, assists, shots, shots_on_target, passes, key_passes, 
            tackles, interceptions, yellow_cards, red_cards
        )
        VALUES (
            %(player_id)s, %(team_id)s, %(season)s, %(competition)s, %(appearances)s, %(starts)s, %(minutes)s, 
            %(goals)s, %(assists)s, %(shots)s, %(shots_on_target)s, %(passes)s, %(key_passes)s, 
            %(tackles)s, %(interceptions)s, %(yellow_cards)s, %(red_cards)s
        )
        ON CONFLICT (player_id, team_id, season, competition) 
        DO UPDATE SET 
            appearances = EXCLUDED.appearances, starts = EXCLUDED.starts, minutes = EXCLUDED.minutes,
            goals = EXCLUDED.goals, assists = EXCLUDED.assists, shots = EXCLUDED.shots,
            shots_on_target = EXCLUDED.shots_on_target, passes = EXCLUDED.passes,
            key_passes = EXCLUDED.key_passes, tackles = EXCLUDED.tackles, 
            interceptions = EXCLUDED.interceptions, yellow_cards = EXCLUDED.yellow_cards, 
            red_cards = EXCLUDED.red_cards;
    """
    execute_batch(cursor, query, statistics)
    logging.info(f"Estadísticas procesadas: {len(statistics)}")

def load_data_to_postgres(transformed_data: dict):
    """
    Orquesta la carga de todos los datos asegurando una transacción completa
    """
    conn = get_db_connection()
    if not conn:
        logging.error("No se pudo establecer conexión para la carga")
        return

    try:
        with conn.cursor() as cursor:
            # 1. Cargamos tablas independientes primero
            load_teams(cursor, transformed_data.get("teams", []))
            load_players(cursor, transformed_data.get("players", []))
            
            # 2. Cargamos tablas dependientes
            load_statistics(cursor, transformed_data.get("statistics", []))
        
        conn.commit()
        logging.info("Carga en PostgreSQL completada con éxito")

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error durante la carga en BD. Haciendo rollback: {error}")
        conn.rollback() 
    finally:
        conn.close()

# Bloque de prueba
if __name__ == "__main__":
    import json
    import os
    from src.transformation.player_transformer import transform_players_data
    
    filepath = os.path.join("data", "raw", "players_real_madrid_2023.json")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
            
        transformed_data = transform_players_data(raw_json)
        
        load_data_to_postgres(transformed_data)
            
    except FileNotFoundError:
        print("Error: No se encontró el archivo RAW")