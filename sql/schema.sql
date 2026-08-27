-- Tabla de Equipos
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100)
);

-- Tabla de Jugadores
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    age INTEGER,
    nationality VARCHAR(100),
    height INTEGER, -- cm
    weight INTEGER  -- kg
);

-- Tabla de Estadísticas
CREATE TABLE IF NOT EXISTS player_statistics (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    team_id INTEGER NOT NULL REFERENCES teams(team_id),
    season INTEGER NOT NULL,
    competition VARCHAR(100) NOT NULL,
    
    -- Métricas de juego
    appearances INTEGER DEFAULT 0,
    starts INTEGER DEFAULT 0,
    minutes INTEGER DEFAULT 0,
    
    -- Métricas ofensivas
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    
    -- Métricas de distribución
    passes INTEGER DEFAULT 0,
    key_passes INTEGER DEFAULT 0,
    
    -- Métricas defensivas y disciplina
    tackles INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,

    -- Restricción UNIQUE para garantizar Idempotencia
    -- Un jugador no puede tener dos registros de estadísticas idénticos para el mismo equipo, temporada y competición
    CONSTRAINT unique_player_season_stats UNIQUE (player_id, team_id, season, competition)
);

-- Crear índices para optimizar futuras consultas analíticas
CREATE INDEX IF NOT EXISTS idx_player_stats_season ON player_statistics(season);
CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_statistics(player_id);