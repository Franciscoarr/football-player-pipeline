import logging
from src.database import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(message)s')

def search_player_in_db(player_name: str):
    """
    Busca un jugador por nombre en PostgreSQL y muestra sus estadísticas
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT p.name, p.age, t.name as team_name, s.competition, s.season, s.goals, s.assists, s.minutes
                FROM players p
                JOIN player_statistics s ON p.player_id = s.player_id
                JOIN teams t ON s.team_id = t.team_id
                WHERE p.name ILIKE %s OR p.firstname ILIKE %s OR p.lastname ILIKE %s
                LIMIT 5;
            """
            search_term = f"%{player_name}%"
            cursor.execute(query, (search_term, search_term, search_term))
            
            results = cursor.fetchall()
            
            if not results:
                print(f"\nNo se encontró a '{player_name}' en la base de datos")
                print("Asegúrate de haber descargado los datos de su equipo primero")
                return

            print(f"\nResultados para '{player_name}':")
            print("-" * 80)
            for row in results:
                name, age, team, comp, season, goals, assists, mins = row
                print(f"{name} ({age} años) | {team} | {comp} ({season})")
                print(f" Estadísticas: {goals} Goles | {assists} Asistencias | {mins} Minutos jugados")
                print("-" * 80)

    except Exception as e:
        logging.error(f"Error al consultar la base de datos: {e}")
    finally:
        conn.close()