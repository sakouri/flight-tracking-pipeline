import json
from pathlib import Path
from kafka import KafkaConsumer

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "live_flights.jsonl"
OUTPUT_FILE.parent.mkdir(exist_ok=True)

consumer = KafkaConsumer(
    "flights",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id=None
)

print("Live consumer started...")

for message in consumer:
    flight = message.value

    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(flight) + "\n")

    print(f"Saved flight {flight['callsign']}")