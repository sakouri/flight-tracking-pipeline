import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
DB_PATH = BASE_DIR / "flights.db"
SQL_PATH = Path(__file__).resolve().parent / "analytics.sql"

con = duckdb.connect(str(DB_PATH))

sql = SQL_PATH.read_text(encoding="utf-8")

for stmt in sql.split(";"):
    stmt = stmt.strip()
    if stmt:
        con.execute(stmt)

con.close()
print("Analytics tables refreshed.")
