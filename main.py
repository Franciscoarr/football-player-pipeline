# main.py
from src.extraction.football_api import search_team_id_by_name
from src.pipeline import run_pipeline
from src.query import search_player_in_db

def print_menu():
    print("\n" + "="*50)
    print("⚽ FOOTBALL PLAYER DATA PIPELINE - MENÚ")
    print("="*50)
    print("1. Descargar datos de un equipo a la Base de Datos")
    print("2. Buscar un jugador en la Base de Datos")
    print("3. Salir")
    print("="*50)

def main():
    while True:
        print_menu()
        opcion = input("Elige una opción (1-3): ")

        if opcion == "1":
            team_name = input("\nIntroduce el nombre del equipo (Ej: FC Barcelona, Real Madrid): ")
            season_input = input("Introduce la temporada (Ej: 2025 o 2025-2026): ")
            
            season = season_input.split("-")[0].strip()
            
            print(f"\nBuscando el equipo '{team_name}' en la API...")
            team_id = search_team_id_by_name(team_name)
            
            if team_id:
                run_pipeline(team_id, int(season))
            else:
                print("No se pudo iniciar la descarga. Revisa el nombre del equipo")

        elif opcion == "2":
            player_name = input("\nIntroduce el nombre del jugador a buscar (Ej: Yamal, Bellingham): ")
            search_player_in_db(player_name)

        elif opcion == "3":
            print("\n¡Gracias por usar Football Player Data Pipeline! Saliendo...\n")
            break
        else:
            print("\nOpción no válida. Por favor, elige 1, 2 o 3")

if __name__ == "__main__":
    main()