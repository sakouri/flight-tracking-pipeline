# Real-Time Flight Tracking Pipeline

**ETL & Pipeline Orchestration — ESILV MSc A4**

## Overview

This project builds a complete end-to-end data pipeline for real-time flight tracking.
Synthetic flight events are generated continuously, streamed through Apache Kafka, stored and transformed in DuckDB, and visualized in a live Streamlit dashboard.

## Architecture

```
producer.py  ──→  [Kafka: topic "flights"]  ──→  consumer_live.py  ──→  DuckDB (raw_flights)
                                                                              │
                                                                    analytics.sql (SQL ELT)
                                                                              │
                                                              ┌───────────────┴──────────────┐
                                                         flight_stats   country_stats   route_stats
                                                                              │
                                                          app_realtime.py (Streamlit dashboard)
```

Batch ETL path (orchestrated with Prefect):
```
[Kafka] → consumer.py → DuckDB → run_analytics.py → analytics tables
                ↑
       orchestrator/pipeline_flow.py (Prefect, scheduled every 60 s)
```

## Technologies

| Layer | Tool |
|---|---|
| Ingestion | Python producer, Apache Kafka |
| Storage | DuckDB |
| Transformation | SQL (analytics.sql) |
| Streaming | Apache Kafka + Python consumer |
| Orchestration | Prefect |
| Visualisation | Streamlit + Plotly |
| Infrastructure | Docker Compose |

## Project Structure

```
flight-tracking-pipeline/
├── producer/producer.py          # Synthetic flight event generator → Kafka
├── consumer/consumer.py          # Batch ETL: Kafka → DuckDB (used by Prefect)
├── consumer/consumer_live.py     # Streaming consumer: Kafka → DuckDB (continuous)
├── sql/analytics.sql             # ELT: raw_flights → flight_stats, country_stats, route_stats
├── sql/run_analytics.py          # Script to run analytics.sql standalone
├── sql/init.sql                  # Table schema reference
├── dashboard/app_realtime.py     # Streamlit dashboard (reads DuckDB, auto-refresh 3s)
├── orchestrator/pipeline_flow.py # Prefect flow orchestrating the batch ETL path
├── airflow/dags/                 # (legacy reference)
├── docker-compose.yml            # Kafka + Zookeeper setup
└── flights.db                    # DuckDB database file
```

## Dashboard Visualisations (5+)

1. Flights by departure airport (bar chart)
2. Live flight positions on world map (scatter geo)
3. Altitude distribution (histogram)
4. Velocity distribution (histogram)
5. Flights by country of origin (pie chart)
6. Top routes (table)
7. Latest flights (table)

## Pipeline Components

### 1. ETL Batch
`consumer.py` reads a batch of messages from Kafka, inserts them into `raw_flights` in DuckDB, then exits. Idempotent: duplicates are skipped via `(icao24, timestamp)` deduplication.

### 2. ELT — SQL Transformations
`analytics.sql` refreshes three analytical tables from `raw_flights`:
- `flight_stats`: global KPIs (total, avg altitude, avg velocity)
- `country_stats`: flights grouped by country
- `route_stats`: flights grouped by departure/arrival airport pair

### 3. Streaming
`consumer_live.py` runs continuously. Uses a fixed Kafka `group_id` so offsets are committed — restarting the consumer never re-reads already-processed messages.

### 4. Orchestration (Prefect)
`pipeline_flow.py` coordinates the batch ETL path with retries and scheduling. Tasks have `retries=3` with backoff.
