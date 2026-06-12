CREATE OR REPLACE TABLE flight_stats AS
SELECT
    COUNT(*) AS total_flights,
    AVG(altitude) AS avg_altitude,
    AVG(velocity) AS avg_velocity
FROM raw_flights;

CREATE OR REPLACE TABLE country_stats AS
SELECT
    origin_country,
    COUNT(*) AS flight_count
FROM raw_flights
GROUP BY origin_country
ORDER BY flight_count DESC;

CREATE OR REPLACE TABLE route_stats AS
SELECT
    departure_airport,
    arrival_airport,
    COUNT(*) AS flight_count
FROM raw_flights
GROUP BY departure_airport, arrival_airport
ORDER BY flight_count DESC;