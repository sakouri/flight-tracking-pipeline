import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Real-Time Flight Tracking", layout="wide")
st_autorefresh(interval=3000, key="autorefresh")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "flights.db"

st.title("✈️ Real-Time Flight Tracking Dashboard")


# ── Helper ────────────────────────────────────────────────────────────────────
def table_exists(con, name: str) -> bool:
    count = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        f"WHERE table_schema='main' AND table_name='{name}'"
    ).fetchone()[0]
    return count > 0


def fetch_all():
    """
    Open DuckDB read-only, fetch all data, close immediately.
    Falls back to inline SQL if analytics tables don't exist yet.
    """
    if not DB_PATH.exists():
        return None, None, None, None

    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        try:
            if not table_exists(con, "raw_flights"):
                return None, None, None, None

            raw = con.execute("SELECT * FROM raw_flights").df()
            if raw.empty:
                return None, None, None, None

            # Use analytics tables if ready, otherwise compute inline
            if table_exists(con, "flight_stats"):
                stats = con.execute("SELECT * FROM flight_stats").df()
            else:
                stats = con.execute("""
                    SELECT COUNT(*) AS total_flights,
                           AVG(altitude) AS avg_altitude,
                           AVG(velocity) AS avg_velocity
                    FROM raw_flights
                """).df()

            if table_exists(con, "route_stats"):
                routes = con.execute(
                    "SELECT * FROM route_stats ORDER BY flight_count DESC LIMIT 10"
                ).df()
            else:
                routes = con.execute("""
                    SELECT departure_airport, arrival_airport, COUNT(*) AS flight_count
                    FROM raw_flights
                    GROUP BY departure_airport, arrival_airport
                    ORDER BY flight_count DESC
                    LIMIT 10
                """).df()

            if table_exists(con, "country_stats"):
                countries = con.execute("SELECT * FROM country_stats").df()
            else:
                countries = con.execute("""
                    SELECT origin_country, COUNT(*) AS flight_count
                    FROM raw_flights
                    GROUP BY origin_country
                    ORDER BY flight_count DESC
                """).df()

        finally:
            con.close()  # Always release the Windows file lock

        return raw, stats, routes, countries

    except Exception as e:
        st.error(f"DB error: {e}")
        return None, None, None, None


# ── Load data ─────────────────────────────────────────────────────────────────
raw, stats, routes, countries = fetch_all()

if raw is None or raw.empty:
    st.warning("⏳ Waiting for flight data — make sure producer.py and consumer_live.py are running.")
    st.info(f"Looking for database at: `{DB_PATH}`")
    st.stop()

# ── KPI metrics ───────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Flights", int(stats["total_flights"].iloc[0]))
col2.metric("Avg Altitude", f"{stats['avg_altitude'].iloc[0]:.0f} m")
col3.metric("Avg Velocity", f"{stats['avg_velocity'].iloc[0]:.0f} km/h")

st.divider()

# ── Row 1: Flights by airport + map ──────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Flights by Departure Airport")
    airport_counts = raw["departure_airport"].value_counts().reset_index()
    airport_counts.columns = ["departure_airport", "flight_count"]
    st.plotly_chart(
        px.bar(airport_counts, x="departure_airport", y="flight_count",
               color="departure_airport"),
        use_container_width=True,
    )

with col_b:
    st.subheader("🗺️ Live Flight Positions")
    st.plotly_chart(
        px.scatter_geo(
            raw, lat="latitude", lon="longitude",
            color="departure_airport", hover_name="callsign",
            projection="natural earth",
        ),
        use_container_width=True,
    )

st.divider()

# ── Row 2: Altitude + Velocity distributions ──────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("📈 Altitude Distribution")
    st.plotly_chart(
        px.histogram(raw, x="altitude", nbins=20,
                     labels={"altitude": "Altitude (m)"}),
        use_container_width=True,
    )

with col_d:
    st.subheader("💨 Velocity Distribution")
    st.plotly_chart(
        px.histogram(raw, x="velocity", nbins=20,
                     color_discrete_sequence=["#EF553B"],
                     labels={"velocity": "Velocity (km/h)"}),
        use_container_width=True,
    )

st.divider()

# ── Row 3: Country pie + Top routes ──────────────────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("🌍 Flights by Country of Origin")
    st.plotly_chart(
        px.pie(countries, names="origin_country", values="flight_count", hole=0.3),
        use_container_width=True,
    )

with col_f:
    st.subheader("🛣️ Top Routes")
    st.dataframe(routes, use_container_width=True, hide_index=True)

st.divider()

# ── Latest flights ────────────────────────────────────────────────────────────
st.subheader("🕐 Latest Flights")
latest = raw.sort_values("timestamp", ascending=False).head(20)
st.dataframe(latest, use_container_width=True, hide_index=True)
