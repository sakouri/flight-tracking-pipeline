"""
orchestrator/pipeline_flow.py
------------------------------
Prefect orchestration for the BATCH ETL component of the pipeline.

Flow:  consumer.py (batch ingest from Kafka → DuckDB)
       → run_analytics.py (run analytics.sql transformations)

This is the scheduled/orchestrated batch path.
The real-time streaming path (consumer_live.py) runs separately and continuously.

Run once:
    python orchestrator/pipeline_flow.py

Schedule (every 60 s, keep terminal open):
    python orchestrator/pipeline_flow.py --loop
"""

import sys
import time
import subprocess
from pathlib import Path
from prefect import flow, task

BASE_DIR = Path(__file__).resolve().parent.parent


@task(retries=3, retry_delay_seconds=5, name="batch_ingest_kafka_to_duckdb")
def load_flights():
    """
    Run consumer.py: reads a batch from Kafka, inserts into DuckDB raw_flights.
    Idempotent: duplicates are skipped via (icao24, timestamp) check.
    Retries up to 3 times if Kafka is temporarily unavailable.
    """
    print("[Task] Starting batch ingest from Kafka...")
    result = subprocess.run(
        ["python", str(BASE_DIR / "consumer" / "consumer.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"consumer.py failed:\n{result.stderr}")
    print(result.stdout)
    print("[Task] Batch ingest complete.")


@task(retries=2, retry_delay_seconds=3, name="run_sql_analytics")
def run_analytics():
    """
    Run analytics.sql via run_analytics.py: refreshes flight_stats,
    country_stats and route_stats from raw_flights.
    """
    print("[Task] Running SQL analytics...")
    result = subprocess.run(
        ["python", str(BASE_DIR / "sql" / "run_analytics.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"run_analytics.py failed:\n{result.stderr}")
    print(result.stdout)
    print("[Task] Analytics complete.")


@flow(name="flight_tracking_batch_pipeline")
def flight_pipeline():
    """
    Batch ETL pipeline:
      1. Ingest a batch from Kafka into DuckDB (idempotent)
      2. Refresh analytical tables from raw data
    """
    load_flights()
    run_analytics()


if __name__ == "__main__":
    loop = "--loop" in sys.argv
    if loop:
        print("[Orchestrator] Running in loop mode (every 60 s). Ctrl+C to stop.")
        while True:
            flight_pipeline()
            time.sleep(60)
    else:
        print("[Orchestrator] Running once.")
        flight_pipeline()
