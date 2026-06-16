import duckdb
from kafka import KafkaConsumer
import json
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "flights.db"

consumer = KafkaConsumer(
    "flights",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=False,
    group_id=None
)

print("Consumer started. Waiting for Kafka messages...")

records = []
start_time = time.time()

while len(records) < 50 and time.time() - start_time < 20:
    messages = consumer.poll(timeout_ms=1000, max_records=50)

    for _, batch in messages.items():
        for msg in batch:
            records.append(msg.value)

consumer.close()

if not records:
    print("No Kafka messages received.")
    exit()

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

for r in records:
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

con.close()

print(f"{len(records)} flights loaded into DuckDB.")