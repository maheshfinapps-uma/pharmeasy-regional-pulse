"""Part 2 — Build SQLite database and validate table integrity."""
from pathlib import Path
import sqlite3
import pandas as pd

BASE = Path(__file__).resolve().parent
DB = BASE / "pharmeasy.db"
ORDERS = BASE / "orders_clean.csv"
MASTER = BASE / "regions_master.csv"

def build_db():
    conn = sqlite3.connect(DB)
    orders = pd.read_csv(ORDERS)
    master = pd.read_csv(MASTER)
    orders.to_sql("orders_clean", conn, if_exists="replace", index=False)
    master.to_sql("regions_master", conn, if_exists="replace", index=False)

    checks = {
        "orders_rows": pd.read_sql("SELECT COUNT(*) n FROM orders_clean", conn).iloc[0,0],
        "master_rows": pd.read_sql("SELECT COUNT(*) n FROM regions_master", conn).iloc[0,0],
        "missing_orders": pd.read_sql(
            "SELECT COUNT(*) n FROM orders_clean WHERE order_id IS NULL OR region IS NULL OR sales_inr IS NULL",
            conn).iloc[0,0],
        "kurnool_order_count": pd.read_sql(
            "SELECT COUNT(order_id) n FROM regions_master m LEFT JOIN orders_clean o ON m.region=o.region WHERE m.region='Kurnool'",
            conn).iloc[0,0],
    }
    print(checks)
    conn.close()

if __name__ == "__main__":
    build_db()
