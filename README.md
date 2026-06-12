# Real-Time Flight Tracking Pipeline

## Overview

This project simulates a real-time flight tracking system.

Synthetic flight data is generated continuously, loaded into a DuckDB database, transformed using SQL, and displayed in a Streamlit dashboard.

## Technologies

* Python
* DuckDB
* Streamlit
* Plotly
* Prefect

## Architecture

Flight Generator => JSONL File => DuckDB => SQL Analytics => Streamlit Dashboard

## Features

* Real-time flight generation
* ETL pipeline
* SQL analytics
* Interactive dashboard
* Workflow orchestration with Prefect

## Dashboard

The dashboard displays:

* Total flights
* Average altitude
* Average velocity
* Flight positions
* Top routes
* Latest flights

## Run the Project

Start the flight generator:

python producer/producer.py

Run the pipeline:

python orchestrator/pipeline_flow.py

Launch the dashboard:

streamlit run dashboard/app.py
