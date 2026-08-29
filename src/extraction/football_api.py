import requests
import json
import os
import logging
from src.config import API_KEY, API_HOST, API_BASE_URL

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_headers():
    """
    Genera los headers necesarios para la autenticación
    """
    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

def fetch_players_by_team(team_id: int, season: int) -> dict:
    """
    Extrae los datos de los jugadores de un equipo en una temporada específica
    """
    endpoint = f"{API_BASE_URL}/players"
    params = {
        "team": team_id,
        "season": season
    }
    
    logging.info(f"Extrayendo jugadores del equipo {team_id} (Temporada {season})...")
    
    try:
        response = requests.get(
            endpoint, 
            headers=get_headers(), 
            params=params, 
            timeout=10
        )
        
        # Levanta una excepción si el código HTTP es 4xx o 5xx
        response.raise_for_status()
        
        data = response.json()
        
        # La API devuelve errores dentro del JSON a veces
        if data.get("errors"):
            logging.error(f"Error de la API: {data['errors']}")
            return None
            
        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error HTTP al conectar con la API: {e}")
        return None

def save_raw_data(data: dict, filename: str):
    """
    Guarda el JSON original en la carpeta data/raw/.
    """
    if not data:
        logging.warning("No hay datos para guardar")
        return
        
    filepath = os.path.join("data", "raw", filename)
    
    # Crea el directorio si por algún motivo no existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    logging.info(f"Datos raw guardados exitosamente en {filepath}")

# Bloque de prueba
if __name__ == "__main__":
    # Probaremos con el Real Madrid (ID: 541) para la temporada 2023
    TEAM_ID = 541
    SEASON = 2023
    
    raw_data = fetch_players_by_team(TEAM_ID, SEASON)
    
    if raw_data:
        save_raw_data(raw_data, "players_real_madrid_2023.json")
        print("\n¡Extracción completada! Revisa la carpeta data/raw/")