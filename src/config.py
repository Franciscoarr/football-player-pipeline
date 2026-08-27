import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
API_HOST = os.getenv("FOOTBALL_API_HOST", "v3.football.api-sports.io")
API_BASE_URL = os.getenv("FOOTBALL_API_BASE_URL", "https://v3.football.api-sports.io")

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

if not API_KEY:
    raise ValueError("ERROR: FOOTBALL_API_KEY no está configurada en el archivo .env")
if not DB_USER or not DB_PASSWORD or not DB_NAME:
    raise ValueError("ERROR: Las credenciales de la base de datos no están configuradas correctamente")