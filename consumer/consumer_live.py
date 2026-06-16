import json
import time
import duckdb
from pathlib import Path
from kafka import KafkaConsumer

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "flights.db"
SQL_PATH = BASE_DIR / "sql" / "analytics.sql"

BATCH_SIZE = 50
SLEEP_SECONDS = 5

KAFKA_GROUP_ID = None  # No group → reads from beginning each restart; DB dedup handles duplicates


def init_db():
    """Create raw_flights table if not exists. Uses (icao24, timestamp) as
    a natural unique key to prevent duplicates at the DB layer too."""
    con = duckdb.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_flights (
            icao24            VARCHAR,
            callsign          VARCHAR,
            departure_airport VARCHAR,
            arrival_airport   VARCHAR,
            origin_country    VARCHAR,
            longitude         DOUBLE,
            latitude          DOUBLE,
            altitude          DOUBLE,
            velocity          DOUBLE,
            on_ground         BOOLEAN,
            timestamp         VARCHAR
        )
    """)
    con.close()
    print(f"[DB] Initialized at {DB_PATH}")


def run_analytics(con):
    """Execute each statement in analytics.sql individually (DuckDB has no executescript)."""
    sql = SQL_PATH.read_text(encoding="utf-8")
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)


def insert_batch(records: list):
    """
    Open DuckDB, insert new records only (deduplication on icao24+timestamp),
    run analytics, close immediately — short lock window, safe on Windows.
    """
    con = duckdb.connect(str(DB_PATH))
    try:
        inserted = 0
        skipped = 0
        for r in records:
            # DB-level idempotence: skip if (icao24, timestamp) already exists
            exists = con.execute(
                "SELECT COUNT(*) FROM raw_flights WHERE icao24 = ? AND timestamp = ?",
                (r.get("icao24"), r.get("timestamp")),
            ).fetchone()[0]

            if exists == 0:
                con.execute(
                    "INSERT INTO raw_flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        r.get("icao24"),
                        r.get("callsign"),
                        r.get("departure_airport"),
                        r.get("arrival_airport"),
                        r.get("origin_country"),
                        r.get("longitude"),
                        r.get("latitude"),
                        r.get("altitude"),
                        r.get("velocity"),
                        r.get("on_ground"),
                        r.get("timestamp"),
                    ),
                )
                inserted += 1
            else:
                skipped += 1

        run_analytics(con)
        total = con.execute("SELECT COUNT(*) FROM raw_flights").fetchone()[0]
        print(f"[DB] +{inserted} inserted, {skipped} duplicates skipped. Total: {total}")
    finally:
        con.close()  # Always release the Windows file lock


def main():
    init_db()

    consumer = KafkaConsumer(
        "flights",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",  # always reads from the start of the topic
        enable_auto_commit=False,
        group_id=None,       # None → no offset tracking; DB dedup prevents duplicates
    )

    print(f"[Kafka] Consumer started (group={KAFKA_GROUP_ID}) — listening on 'flights'...")

    while True:
        messages = consumer.poll(timeout_ms=2000, max_records=BATCH_SIZE)

        batch = []
        for _, msg_list in messages.items():
            for msg in msg_list:
                batch.append(msg.value)

        if batch:
            insert_batch(batch)
        else:
            print("[Kafka] No new messages, sleeping...")

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
