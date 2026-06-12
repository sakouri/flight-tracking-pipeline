CREATE TABLE IF NOT EXISTS raw_flights (
    id SERIAL PRIMARY KEY,
    icao24 TEXT,
    callsign TEXT,
    origin_country TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    on_ground BOOLEAN,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flight_stats (
    id SERIAL PRIMARY KEY,
    stat_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_flights INTEGER,
    avg_altitude DOUBLE PRECISION,
    avg_velocity DOUBLE PRECISION
);