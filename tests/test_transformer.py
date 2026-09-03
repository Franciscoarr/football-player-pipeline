import pytest
from src.transformation.player_transformer import clean_measurement, transform_players_data

def test_clean_measurement_valid_strings():
    # Prueba que los strings normales se convierten en enteros
    assert clean_measurement("185 cm") == 185
    assert clean_measurement("75 kg") == 75
    assert clean_measurement(" 190cm ") == 190

def test_clean_measurement_nulls_and_empty():
    # Prueba el manejo de nulos (programación defensiva)
    assert clean_measurement(None) is None
    assert clean_measurement("") is None

def test_clean_measurement_invalid_data():
    # Prueba qué pasa si la API envía un texto sin números
    assert clean_measurement("desconocido") is None
    assert clean_measurement("N/A") is None

def test_transform_players_data_structure():
    # Prueba que el transformador estructura correctamente el JSON crudo
    # Simulamos (Mock) un JSON de la API
    mock_raw_data = {
        "response": [
            {
                "player": {
                    "id": 1,
                    "name": "Test Player",
                    "height": "180 cm",
                    "weight": "75 kg"
                },
                "statistics": [
                    {
                        "team": {"id": 100, "name": "Test Team"},
                        "league": {
                            "name": "Test League",
                            "country": "Spain",
                            "season": 2023,
                        },
                        "goals": {"total": 5},
                        "games": {"appearences": 10}
                    }
                ]
            }
        ]
    }

    result = transform_players_data(mock_raw_data)

    # Comprobamos que generó las 3 listas correctamente
    assert len(result["players"]) == 1
    assert len(result["teams"]) == 1
    assert len(result["statistics"]) == 1
    
    # Comprobamos que la limpieza se aplicó dentro de la transformación
    assert result["players"][0]["height"] == 180
    assert result["statistics"][0]["goals"] == 5
    assert result["teams"][0]["country"] == "Spain"