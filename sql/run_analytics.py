import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).parent

con = duckdb.connect("flights.db")

sql_file = BASE_DIR / "analytics.sql"

with open(sql_file, "r", encoding="utf-8") as f:
    sql = f.read()

con.execute(sql)

print("Analytics tables created.")