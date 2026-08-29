import logging
import time
from src.extraction.football_api import fetch_players_by_team, save_raw_data
from src.transformation.player_transformer import transform_players_data
from src.loading.postgres_loader import load_data_to_postgres

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_pipeline(team_id: int, season: int):
    """
    Ejecuta el pipeline ETL completo para un equipo y temporada.
    """
    logging.info("==================================================")
    logging.info(f"Iniciando Football Player Pipeline")
    logging.info(f"Equipo ID: {team_id} | Temporada: {season}")
    logging.info("==================================================")

    start_time = time.time()

    # 1. EXTRACT
    logging.info("Extrayendo datos de la API...")
    raw_data = fetch_players_by_team(team_id, season)
    
    if not raw_data:
        logging.error("Fallo en la extracción. Deteniendo el pipeline")
        return

    # 2. SAVE RAW DATA
    logging.info("Guardando datos RAW...")
    filename = f"players_team_{team_id}_{season}.json"
    save_raw_data(raw_data, filename)

    # 3. TRANSFORM
    logging.info("Transformando datos...")
    transformed_data = transform_players_data(raw_data)
    
    if not transformed_data["players"]:
        logging.warning("No se encontraron jugadores para procesar tras la transformación")
        return

    # 4. LOAD
    logging.info("Cargando datos en PostgreSQL...")
    load_data_to_postgres(transformed_data)

    elapsed_time = round(time.time() - start_time, 2)
    logging.info("==================================================")
    logging.info(f"Pipeline completado exitosamente en {elapsed_time} segundos")
    logging.info("==================================================")

if __name__ == "__main__":
    # Datos iniciales (Real Madrid - Temporada 2023)
    TARGET_TEAM_ID = 541
    TARGET_SEASON = 2023
    
    run_pipeline(TARGET_TEAM_ID, TARGET_SEASON)