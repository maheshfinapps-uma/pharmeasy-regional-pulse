"""Part 2 — SQL JOIN validation and verified metrics with printed output."""
from pathlib import Path
import sqlite3
import pandas as pd

DB = Path(__file__).resolve().parent / "pharmeasy.db"

def run_queries():
    conn = sqlite3.connect(DB)

    join_check = pd.read_sql("""
        SELECT
            (SELECT COUNT(*) FROM regions_master) AS master_rows,
            COUNT(*) AS left_join_rows,
            COUNT(order_id) AS matched_orders
        FROM regions_master m
        LEFT JOIN orders_clean o ON m.region = o.region
    """, conn)
    print("\nJOIN VALIDATION")
    print(join_check.to_string(index=False))

    dup = pd.read_sql("""
        SELECT order_id, COUNT(*) AS n
        FROM orders_clean
        GROUP BY order_id
        HAVING COUNT(*) > 1
    """, conn)
    print("\nDUPLICATE ORDER-ID GROUPS")
    print(dup.to_string(index=False) if not dup.empty else "0 duplicate groups")

    monthly = pd.read_sql("""
        SELECT region,
               strftime('%Y-%m', order_date) AS month,
               ROUND(SUM(sales_inr), 2) AS sales_inr,
               COUNT(DISTINCT order_id) AS distinct_orders
        FROM orders_clean
        GROUP BY region, month
        ORDER BY region, month
    """, conn)
    print("\nMONTHLY SALES")
    print(monthly.to_string(index=False))

    pivot = monthly.pivot(index="region", columns="month", values="sales_inr").fillna(0)
    for month in ["2026-05", "2026-06"]:
        prev = "2026-04" if month == "2026-05" else "2026-05"
        pivot[f"{prev}_to_{month}_pct"] = (
            (pivot[month] - pivot[prev]) / pivot[prev].replace(0, pd.NA) * 100
        )
    print("\nMONTH-OVER-MONTH")
    print(pivot.round(2).to_string())

    conn.close()

if __name__ == "__main__":
    run_queries()
