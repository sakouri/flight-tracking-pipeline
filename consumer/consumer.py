import duckdb
from kafka import KafkaConsumer
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "flights.db"

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE TABLE IF NOT EXISTS raw_flights (
    icao24 VARCHAR,
    callsign VARCHAR,
    departure_airport VARCHAR,
    arrival_airport VARCHAR,
    origin_country VARCHAR,
    longitude DOUBLE,
    latitude DOUBLE,
    altitude DOUBLE,
    velocity DOUBLE,
    on_ground BOOLEAN,
    timestamp TIMESTAMP
);
""")

consumer = KafkaConsumer(
    "flights",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="flight_consumer_group"
)

print("Consumer started. Reading from Kafka...")

for message in consumer:
    r = message.value

    con.execute("""
    INSERT INTO raw_flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        r["icao24"],
        r["callsign"],
        r["departure_airport"],
        r["arrival_airport"],
        r["origin_country"],
        r["longitude"],
        r["latitude"],
        r["altitude"],
        r["velocity"],
        r["on_ground"],
        r["timestamp"]
    ))

    print(f"Inserted flight {r['callsign']}")