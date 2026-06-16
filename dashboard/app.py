import streamlit as st
import duckdb
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

st.set_page_config(page_title="Flight Tracking Dashboard", layout="wide")
st_autorefresh(interval=10000, key="refresh")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "flights.db"

con = duckdb.connect(str(DB_PATH))

flight_stats = con.sql("SELECT * FROM flight_stats").fetchdf()
country_stats = con.sql("SELECT * FROM country_stats").fetchdf()
route_stats = con.sql("SELECT * FROM route_stats").fetchdf()

flights = con.sql("""
SELECT *
FROM raw_flights
ORDER BY timestamp DESC
""").fetchdf()

recent_flights = flights.head(20)

st.title("Real-Time Flight Tracking Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Flights", int(flight_stats["total_flights"][0]))
col2.metric("Average Altitude", f"{flight_stats['avg_altitude'][0]:.0f} m")
col3.metric("Average Velocity", f"{flight_stats['avg_velocity'][0]:.0f} km/h")

st.subheader("Flights by Departure Airport")

fig_country = px.bar(
    country_stats,
    x="origin_country",
    y="flight_count"
)
st.plotly_chart(fig_country, use_container_width=True)

st.subheader("Flight Positions")

fig_map = px.scatter_geo(
    flights,
    lat="latitude",
    lon="longitude",
    color="departure_airport",
    hover_name="callsign"
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Altitude Distribution")

fig_alt = px.histogram(
    flights,
    x="altitude",
    nbins=20
)
st.plotly_chart(fig_alt, use_container_width=True)

st.subheader("Top Routes")
st.dataframe(route_stats.head(10), use_container_width=True)

st.subheader("Latest Flights")
st.dataframe(recent_flights, use_container_width=True)