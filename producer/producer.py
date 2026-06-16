import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "flights"

routes = [
    ("Paris", "London", 48.8566, 2.3522, 51.5074, -0.1278),
    ("Madrid", "Rome", 40.4168, -3.7038, 41.9028, 12.4964),
    ("Amsterdam", "Berlin", 52.3676, 4.9041, 52.5200, 13.4050),
    ("Lisbon", "Paris", 38.7223, -9.1393, 48.8566, 2.3522),
    ("Milan", "Barcelona", 45.4642, 9.1900, 41.3874, 2.1686),
]

airlines = ["AF", "BA", "LH", "IB", "KL", "AZ"]

while True:
    for _ in range(50):
        dep, arr, lat1, lon1, lat2, lon2 = random.choice(routes)
        progress = random.random()

        flight = {
            "icao24": f"{random.randint(100000, 999999)}",
            "callsign": f"{random.choice(airlines)}{random.randint(100, 999)}",
            "departure_airport": dep,
            "arrival_airport": arr,
            "origin_country": dep,
            "longitude": lon1 + (lon2 - lon1) * progress,
            "latitude": lat1 + (lat2 - lat1) * progress,
            "altitude": random.uniform(8000, 12000),
            "velocity": random.uniform(650, 950),
            "on_ground": False,
            "timestamp": datetime.now().isoformat()
        }

        producer.send(TOPIC, flight)

    producer.flush()
    print("50 flights sent to Kafka")
    time.sleep(10)