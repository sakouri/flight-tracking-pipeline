import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Real-Time Flight Dashboard", layout="wide")
st_autorefresh(interval=3000, key="refresh")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "live_flights.jsonl"

st.title("✈️ Real-Time Flight Tracking Dashboard")

if not DATA_FILE.exists():
    st.warning("Waiting for consumer data...")
    st.stop()

rows = []

with DATA_FILE.open("r", encoding="utf-8") as f:
    for line in f.readlines()[-1000:]:
        if line.strip():
            rows.append(json.loads(line))

if not rows:
    st.warning("Waiting for flight data...")
    st.stop()

df = pd.DataFrame(rows)

col1, col2, col3 = st.columns(3)

col1.metric("Total Flights Received", len(df))
col2.metric("Average Altitude", f"{df['altitude'].mean():.0f} m")
col3.metric("Average Velocity", f"{df['velocity'].mean():.0f} km/h")

st.subheader("Flights by Departure Airport")

airport_counts = df["departure_airport"].value_counts().reset_index()
airport_counts.columns = ["departure_airport", "flight_count"]

st.plotly_chart(
    px.bar(airport_counts, x="departure_airport", y="flight_count"),
    width="stretch"
)

st.subheader("Flight Positions")

st.plotly_chart(
    px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color="departure_airport",
        hover_name="callsign"
    ),
    width="stretch"
)

st.subheader("Altitude Distribution")

st.plotly_chart(
    px.histogram(df, x="altitude", nbins=20),
    width="stretch"
)

st.subheader("Top Routes")

routes = (
    df.groupby(["departure_airport", "arrival_airport"])
    .size()
    .reset_index(name="flight_count")
    .sort_values("flight_count", ascending=False)
)

st.dataframe(routes.head(10), width="stretch")

st.subheader("Latest Flights")

st.dataframe(df.tail(20).sort_values("timestamp", ascending=False), width="stretch")