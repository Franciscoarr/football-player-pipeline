import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clean_measurement(value: str) -> int:
    """
    Convierte strings como '185 cm' o '75 kg' en enteros
    Retorna None si el valor es inválido o nulo
    """
    if not value or not isinstance(value, str):
        return None
    
    digits = ''.join(filter(str.isdigit, value))
    return int(digits) if digits else None

def transform_players_data(raw_data: dict) -> dict:
    """
    Recibe el JSON crudo de la API y lo separa en listas de diccionarios
    limpios para equipos, jugadores y estadísticas
    """
    teams = {}
    players = {}
    statistics = []

    responses = raw_data.get("response", [])
    
    for item in responses:
        player_info = item.get("player", {})
        stats_list = item.get("statistics", [])
        
        # 1. Transformar Jugador
        player_id = player_info.get("id")
        if not player_id:
            continue
            
        players[player_id] = {
            "player_id": player_id,
            "name": player_info.get("name"),
            "firstname": player_info.get("firstname"),
            "lastname": player_info.get("lastname"),
            "age": player_info.get("age"),
            "nationality": player_info.get("nationality"),
            "height": clean_measurement(player_info.get("height")),
            "weight": clean_measurement(player_info.get("weight"))
        }
        
        # 2. Transformar Equipos y Estadísticas
        for stat in stats_list:
            team_info = stat.get("team", {})
            league_info = stat.get("league", {})
            games = stat.get("games", {})
            goals = stat.get("goals", {})
            shots = stat.get("shots", {})
            passes = stat.get("passes", {})
            tackles = stat.get("tackles", {})
            cards = stat.get("cards", {})
            
            team_id = team_info.get("id")
            
            if team_id and team_id not in teams:
                teams[team_id] = {
                    "team_id": team_id,
                    "name": team_info.get("name"),
                    "country": None # La API en este endpoint a veces no da el país del equipo
                }
            
            if team_id and league_info.get("name"):
                statistics.append({
                    "player_id": player_id,
                    "team_id": team_id,
                    "season": league_info.get("season"),
                    "competition": league_info.get("name"),
                    
                    # Usamos 'or 0' para convertir posibles None en 0 
                    "appearances": games.get("appearences") or 0, 
                    "starts": games.get("lineups") or 0,
                    "minutes": games.get("minutes") or 0,
                    "goals": goals.get("total") or 0,
                    "assists": goals.get("assists") or 0,
                    "shots": shots.get("total") or 0,
                    "shots_on_target": shots.get("on") or 0,
                    "passes": passes.get("total") or 0,
                    "key_passes": passes.get("key") or 0,
                    "tackles": tackles.get("total") or 0,
                    "interceptions": tackles.get("interceptions") or 0,
                    "yellow_cards": cards.get("yellow") or 0,
                    "red_cards": cards.get("red") or 0
                })

    logging.info(f"Transformación completada: {len(players)} jugadores, {len(teams)} equipos, {len(statistics)} registros de estadísticas")
    
    return {
        "teams": list(teams.values()),
        "players": list(players.values()),
        "statistics": statistics
    }

# Bloque de prueba
if __name__ == "__main__":
    import os
    
    filepath = os.path.join("data", "raw", "players_real_madrid_2023.json")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
            
        transformed_data = transform_players_data(raw_json)
        
        # Imprimimos un jugador y una estadística de ejemplo para verificar
        if transformed_data["players"]:
            print("\nEjemplo de jugador limpio:")
            print(transformed_data["players"][0])
            
        if transformed_data["statistics"]:
            print("\nEjemplo de estadística limpia:")
            print(transformed_data["statistics"][0])
            
    except FileNotFoundError:
        print("Error: No se encontró el archivo RAW")