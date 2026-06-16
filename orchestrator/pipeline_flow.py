from prefect import flow, task
import subprocess
import time

@task
def load_flights():
    subprocess.run(["python", "consumer/consumer.py"], check=True)

@task
def run_analytics():
    subprocess.run(["python", "sql/run_analytics.py"], check=True)

@flow(name="flight_tracking_pipeline")
def flight_pipeline():
    load_flights()
    run_analytics()

if __name__ == "__main__":
    while True:
        flight_pipeline()
        time.sleep(10)