# Setup & Launch Guide

## Prerequisites

- Python 3.9+
- Docker Desktop (for Kafka)

## 1. Install Python dependencies

```bash
pip install kafka-python duckdb pandas plotly streamlit streamlit-autorefresh prefect
```

## 2. Start Kafka (Docker)

```bash
docker-compose up -d
```

Wait ~15 seconds for Kafka and Zookeeper to be ready.

## 3. Launch order for the demo

Open **4 terminals** from the project root:

```bash
# Terminal 1 — Producer (generates synthetic flight events → Kafka)
python producer/producer.py

# Terminal 2 — Live consumer (Kafka → DuckDB → analytics, runs continuously)
python consumer/consumer_live.py

# Terminal 3 — Dashboard (reads DuckDB, auto-refresh every 3 s)
streamlit run dashboard/app_realtime.py

# Terminal 4 (optional) — Batch ETL orchestrated by Prefect
python orchestrator/pipeline_flow.py --loop
```

Wait ~10 seconds after starting Terminal 2 before opening the dashboard.

## 4. Stopping

```bash
# Stop Kafka
docker-compose down

# Ctrl+C in each terminal
```

## 5. Reset the database

Delete `flights.db` to start fresh:

```bash
del flights.db        # Windows
rm flights.db         # Mac/Linux
```

The consumer will recreate the table on next start.

## Notes

- The project uses **absolute paths** derived from `Path(__file__).resolve().parent.parent`,
  so it works correctly regardless of which directory you run the scripts from.
- DuckDB is opened in **read-only mode** by the dashboard to avoid Windows file-locking conflicts.
- The consumer uses a fixed Kafka `group_id` (`flight_consumer_live`) so restarting it
  never re-reads already-processed messages (idempotent).
