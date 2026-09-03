# Football Player Data Pipeline

Este proyecto es un pipeline ETL (Extract, Transform, Load) para obtener información de jugadores de fútbol desde la API de Api-Football, transformarla y almacenarla en PostgreSQL para su consulta posterior.

Está pensado para automatizar la extracción de datos de un equipo y temporada concreta, normalizar la información y dejarla lista para análisis o consultas rápidas desde la base de datos.

## ¿Qué hace este proyecto?

El flujo principal es:

1. Busca un equipo por nombre en la API.
2. Obtiene los jugadores del equipo para una temporada determinada.
3. Guarda el JSON original en la carpeta data/raw.
4. Transforma los datos para normalizarlos en estructuras útiles.
5. Carga los equipos, jugadores y estadísticas en PostgreSQL.
6. Permite consultar jugadores desde la base de datos.
7. Incluye un dashboard interactivo para analizar los datos.

## Tecnologías utilizadas

- Python 3
- Requests: para consumir la API REST
- PostgreSQL: almacenamiento de la información
- Docker + Docker Compose: para levantar la base de datos
- psycopg2-binary: conexión con PostgreSQL desde Python
- Streamlit y Altair: dashboard y gráficos interactivos
- python-dotenv: manejo de variables de entorno
- Pytest: pruebas unitarias

## Estructura del proyecto

```text
football-player-pipeline/
├── data/
│   └── raw/
│       └── ... archivos JSON descargados de la API
├── src/
│   ├── config.py
│   ├── database.py
│   ├── pipeline.py
│   ├── query.py
│   ├── extraction/
│   │   └── football_api.py
│   ├── loading/
│   │   └── postgres_loader.py
│   ├── dashboard/
│   │   └── app.py
│   └── transformation/
│       └── player_transformer.py
├── sql/
│   └── schema.sql
├── tests/
│   └── test_transformer.py
├── .env.example
├── docker-compose.yml
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Descripción de los módulos

### 1. main.py

Es el punto de entrada del proyecto. Muestra un menú interactivo con dos funciones principales:

- Descargar datos de un equipo a la base de datos.
- Buscar un jugador por nombre dentro de la base de datos.

Ejecuta el programa con:

```bash
python main.py
```

---

### 2. src/config.py

Aquí se cargan las variables de entorno para la API de fútbol y PostgreSQL.

Variables esperadas:

- FOOTBALL_API_KEY
- FOOTBALL_API_HOST
- FOOTBALL_API_BASE_URL
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT

Si la clave de la API no está configurada, el programa lanza un error al inicio.

---

### 3. src/extraction/football_api.py

Este módulo se encarga de la extracción desde Api-Football.

Funciones principales:

- get_headers(): genera los headers con la clave de la API.
- fetch_players_by_team(team_id, season, max_pages=3): consulta los jugadores de un equipo/temporada, recorriendo las páginas disponibles hasta el límite permitido por el plan gratuito.
- save_raw_data(data, filename): guarda el JSON bruto en data/raw.
- search_team_id_by_name(team_name): busca un equipo por nombre y devuelve su ID oficial.

Este módulo es la parte que comunica el proyecto con la API externa.

---

### 4. src/transformation/player_transformer.py

Recibe el JSON crudo de la API y lo convierte en estructuras más limpias para insertar en la base de datos.

Convierte los datos en tres listas:

- teams
- players
- statistics

Además, normaliza medidas como altura y peso, por ejemplo:

- "180 cm" -> 180
- "75 kg" -> 75
- "N/A" o vacío -> None

El país del equipo se obtiene de `team.country` cuando está disponible. En la
respuesta del endpoint de jugadores de Api-Football normalmente aparece en
`league.country`, por lo que se utiliza como respaldo para evitar que el campo
`country` quede vacío.

Esto facilita la carga posterior en PostgreSQL.

---

### 5. src/loading/postgres_loader.py

Se encarga de insertar o actualizar los registros en PostgreSQL.

Carga en tres pasos:

- equipos
- jugadores
- estadísticas

Usa inserciones idempotentes con ON CONFLICT para evitar duplicados.

---

### 6. src/database.py

Maneja la conexión con PostgreSQL.

Define la función:

- get_db_connection(): devuelve una conexión activa a la base de datos.

---

### 7. src/query.py

Permite hacer consultas a la base de datos para buscar jugadores y visualizar sus estadísticas.

Consulta ejemplo:

- nombre del jugador
- edad
- equipo
- competición
- temporada
- goles
- asistencias
- minutos

---

### 8. src/pipeline.py

Es el orquestador del ETL.

Ejecuta este flujo:

1. extracción de la API
2. guardado del JSON raw
3. transformación de los datos
4. carga a PostgreSQL

---

### 9. src/dashboard/app.py

Contiene un dashboard desarrollado con Streamlit y conectado a PostgreSQL.

Permite filtrar los datos por:

- equipo
- temporada
- competición

Muestra indicadores generales y gráficos interactivos con el Top 5 de:

- goleadores
- asistentes
- tarjetas amarillas
- tarjetas rojas
- minutos disputados
- partidos jugados

Los gráficos seleccionan los cinco valores más altos y los ordenan de mayor a
menor según la métrica representada. También incluye una tabla detallada con
los registros filtrados.

Para iniciar el dashboard:

```bash
streamlit run src/dashboard/app.py
```

---

### 10. sql/schema.sql

Define la base de datos del proyecto.

Tablas creadas:

- teams
- players
- player_statistics

Incluye índices para optimizar búsquedas por temporada y jugador.

---

### 11. tests/test_transformer.py

Contiene pruebas unitarias para validar:

- conversión de medidas a enteros
- manejo de valores nulos o vacíos
- estructura final de la transformación

---

## Base de datos

Este proyecto usa PostgreSQL con una estructura simple pero útil para análisis deportivos.

### Tablas principales

#### teams

Guarda información de cada equipo:

- team_id
- name
- country

#### players

Guarda datos personales básicos:

- player_id
- name
- firstname
- lastname
- age
- nationality
- height
- weight

#### player_statistics

Guarda los datos estadísticos por temporada y competición:

- player_id
- team_id
- season
- competition
- appearances
- starts
- minutes
- goals
- assists
- shots
- shots_on_target
- passes
- key_passes
- tackles
- interceptions
- yellow_cards
- red_cards

---

## Cómo levantar la base de datos con Docker

En la raíz del proyecto existe un archivo docker-compose.yml.

Puedes iniciar la base de datos con:

```bash
docker-compose up -d
```

Luego, para crear la estructura SQL:

```bash
docker exec -i football_postgres psql -U pipeline_user -d football_db < sql/schema.sql
```

Esto crea la base de datos y sus tablas necesarias.

---

## Variables de entorno

Debes crear un archivo .env con algo similar a esto:

```env
FOOTBALL_API_KEY=tu_clave_api
FOOTBALL_API_HOST=v3.football.api-sports.io
FOOTBALL_API_BASE_URL=https://v3.football.api-sports.io

POSTGRES_DB=football_db
POSTGRES_USER=pipeline_user
POSTGRES_PASSWORD=pipeline_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

> Importante: la API de Api-Football necesita una clave válida. Si no se configura, el proyecto no arrancará correctamente.

---

## Instalación

1. Clona el proyecto.
2. Crea un entorno virtual.
3. Instala las dependencias.

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

---

## Uso del proyecto

### Iniciar la aplicación

```bash
python main.py
```

### Menú disponible

1. Descargar datos de un equipo a la Base de Datos
2. Buscar un jugador en la Base de Datos
3. Salir

Ejemplo de uso:

- Equipo: Barcelona
- Temporada: 2024

El programa buscará el ID del equipo, extraerá sus jugadores y los cargará a PostgreSQL.

---

## Flujo ETL detallado

### Extract

La API se consulta por equipo y temporada, con el endpoint:

```text
https://v3.football.api-sports.io/players
```

Se envían parámetros como:

- team
- season
- page

### Transform

Se normaliza la estructura recibida por la API para formar entidades consistentes:

- equipo
- jugador
- estadísticas

### Load

Se insertan los resultados en PostgreSQL usando transacciones y upserts para mantener la base de datos actualizada.

---

## Limitaciones importantes

### 1. Límite del plan gratuito de Api-Football

La API de Api-Football tiene un límite de paginación en su plan gratuito.

Por ejemplo, si un equipo tiene más de 3 páginas de jugadores, la API puede devolver solo hasta 3 páginas en ese plan. Esto implica que no se va a obtener el total completo de jugadores de ese equipo en todos los casos.

El proyecto está preparado para:

- recorrer páginas hasta el máximo permitido
- detectar si la extracción fue parcial
- registrar un warning cuando no se puede obtener todo

Esto significa que la extracción puede quedar incompleta si el equipo supera el límite del plan.

### 2. Dependencia externa

El proyecto depende totalmente de la disponibilidad y de la estructura de la API externa.

Si la API:

- cambia el formato del JSON
- bloquea peticiones
- falla por cuota o rate limit
- requiere autenticación adicional

el pipeline podría romperse o devolver datos incompletos.

### 3. Búsqueda por nombre de equipo

La búsqueda de equipo usa search_team_id_by_name(team_name) y toma el primer resultado que devuelve la API. Esto puede fallar si hay varios equipos con nombres similares o si el nombre ingresado no coincide exactamente.

### 4. Uso de un equipo concreto

El pipeline está orientado a extraer un equipo y su temporada, no a obtener todo el calendario mundial en una sola ejecución.

### 5. No hay caché ni reintentos avanzados

Actualmente no hay un sistema robusto de reintentos con backoff ni manejo de errores de red más sofisticado.

---

## Casos de uso

Este proyecto sirve para:

- recopilar datos de jugadores por equipo y temporada
- crear una base de datos histórica de estadísticas
- consultar jugadores con sus estadísticas por competición
- construir análisis deportivos y dashboards
- soportar pruebas o prototipos de analítica de fútbol

---

## Posibles mejoras futuras

- soporte para múltiples equipos en una sola ejecución
- manejo avanzado de reintentos y backoff
- almacenamiento de metadatos de extracción
- exportación a CSV o parquet
- dashboard con Streamlit o FastAPI
- soporte para más competiciones o temporadas
- manejo de equipos con más de 3 páginas mediante plan pago

---

## Resumen

Este proyecto combina extracción, transformación, almacenamiento y consulta para crear una pequeña base de datos de jugadores de fútbol a partir de Api-Football.

Es útil como pipeline ETL básico, con una estructura clara y modular, pero tiene limitaciones importantes por el plan gratuito de la API y por depender de una fuente externa.

---

## Autor / proyecto

Proyecto desarrollado como pipeline de datos para football analytics con Python y PostgreSQL.

Si quieres ampliar el proyecto, puedes:

- añadir más campos de estadísticas
- automatizar más equipos
- crear una interfaz web
- guardar más metadatos de extracción
