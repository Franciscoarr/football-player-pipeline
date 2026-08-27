import psycopg2
from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

def get_db_connection():
    """
    Crea y devuelve una conexión a la base de datos PostgreSQL
    """
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return connection
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        raise

if __name__ == "__main__":
    print("Probando la conexión a PostgreSQL...")
    conn = get_db_connection()
    if conn:
        print("¡Conexión exitosa a la base de datos!")
        conn.close()