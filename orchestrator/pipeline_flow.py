from prefect import flow, task
import subprocess

@task
def load_flights():
    subprocess.run(["python", "consumer/consumer.py"])

@task
def run_analytics():
    subprocess.run(["python", "sql/run_analytics.py"])

@flow(name="flight_tracking_pipeline")
def flight_pipeline():

    load_flights()

    run_analytics()

if __name__ == "__main__":
    flight_pipeline()