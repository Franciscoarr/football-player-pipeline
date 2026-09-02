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

def fetch_players_by_team(team_id: int, season: int, max_pages: int = 3) -> dict:
    """
    Extrae los jugadores de un equipo y temporada recorriendo hasta el máximo
    permitido por el plan gratuito.
    """
    endpoint = f"{API_BASE_URL}/players"
    all_players = []
    current_page = 1
    total_pages = 1
    limit_reached = False

    logging.info(f"Extrayendo jugadores del equipo {team_id} (Temporada {season})...")

    try:
        while current_page <= max_pages:
            params = {
                "team": team_id,
                "season": season,
                "page": current_page
            }

            response = requests.get(
                endpoint,
                headers=get_headers(),
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                logging.error(f"Error de la API: {data['errors']}")
                return None

            page_response = data.get("response", [])
            if not page_response:
                break

            all_players.extend(page_response)

            paging = data.get("paging") or {}
            total_pages = int(paging.get("total", current_page) or current_page)

            if total_pages > max_pages:
                limit_reached = True
                logging.warning(
                    "La API reporta más de %s páginas para este equipo, pero el plan gratuito solo permite %s. "
                    "Se devolverá una extracción parcial.",
                    max_pages,
                    max_pages,
                )

            if current_page >= min(total_pages, max_pages):
                break

            current_page += 1

        if not all_players:
            return None

        partial_data = {
            "get": "players",
            "parameters": {
                "team": str(team_id),
                "season": str(season)
            },
            "errors": [],
            "results": len(all_players),
            "paging": {
                "current": min(current_page, max_pages),
                "total": min(total_pages, max_pages)
            },
            "limit_reached": limit_reached,
            "response": all_players
        }

        return partial_data

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

def search_team_id_by_name(team_name: str) -> int:
    """
    Busca un equipo por su nombre y devuelve su ID oficial de la API
    """
    endpoint = f"{API_BASE_URL}/teams"
    params = {"search": team_name}
    
    try:
        response = requests.get(endpoint, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("response", [])
        if not results:
            logging.error(f"No se encontró ningún equipo con el nombre '{team_name}'")
            return None
            
        team_id = results[0]["team"]["id"]
        exact_name = results[0]["team"]["name"]
        logging.info(f"Equipo encontrado: {exact_name} (ID: {team_id})")
        
        return team_id

    except requests.exceptions.RequestException as e:
        logging.error(f"Error al buscar el equipo: {e}")
        return None

# Bloque de prueba
if __name__ == "__main__":
    # Probaremos con el Real Madrid (ID: 541) para la temporada 2023
    TEAM_ID = 541
    SEASON = 2023
    
    raw_data = fetch_players_by_team(TEAM_ID, SEASON)
    
    if raw_data:
        save_raw_data(raw_data, "players_real_madrid_2023.json")
        print("\n¡Extracción completada! Revisa la carpeta data/raw/")