"""
Part 1 — Deterministic PharmaEasy dataset generator.

Creates:
  pharmeasy_orders_raw.csv  : 2,159 rows (2,100 analytical rows + 59 exact duplicates)
  regions_master.csv        : 10 regions (9 active + Kurnool inactive)

The analytical 2,100 rows are generated with fixed seed 2026 and the
April–June regional sales totals used by the assessment metrics.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)
OUT = Path(__file__).resolve().parent

REGIONS = [
    "Hyderabad", "Warangal", "Vijayawada", "Visakhapatnam", "Guntur",
    "Nellore", "Tirupati", "Karimnagar", "Bengaluru", "Kurnool"
]
ACTIVE = REGIONS[:-1]
CATEGORIES = [
    "Lab Tests", "Medical Devices", "OTC Medicines", "Personal Care",
    "Prescription Medicines", "Wellness & Nutrition"
]
PRODUCTS = {
    "Lab Tests": ["CBC Test", "Lipid Profile", "HbA1c Test"],
    "Medical Devices": ["BP Monitor", "Glucometer", "Thermometer"],
    "OTC Medicines": ["Paracetamol", "Antacid", "Cough Syrup"],
    "Personal Care": ["Face Wash", "Moisturizer", "Hand Wash"],
    "Prescription Medicines": ["Amoxicillin", "Metformin", "Atorvastatin"],
    "Wellness & Nutrition": ["Vitamin C", "Protein Powder", "Multivitamin"],
}
MARGINS = {
    "Lab Tests": 0.148328,
    "Medical Devices": 0.152795,
    "OTC Medicines": 0.148938,
    "Personal Care": 0.147893,
    "Prescription Medicines": 0.151463,
    "Wellness & Nutrition": 0.150877,
}

TARGETS = {
    "Bengaluru": [203505.48, 172929.68, 170294.11],
    "Guntur": [62442.27, 138738.93, 99745.18],
    "Hyderabad": [209670.15, 243825.28, 294088.56],
    "Karimnagar": [49815.71, 61585.90, 34490.58],
    "Kurnool": [0.00, 0.00, 0.00],
    "Nellore": [85623.19, 91184.86, 94393.62],
    "Tirupati": [54582.74, 91083.20, 75530.99],
    "Vijayawada": [171334.19, 174863.57, 153849.68],
    "Visakhapatnam": [134765.29, 50590.08, 100735.57],
    "Warangal": [100468.14, 78339.23, 66715.24],
}
COUNTS = {
    "Bengaluru": 234, "Guntur": 234, "Hyderabad": 234, "Karimnagar": 234,
    "Nellore": 234, "Tirupati": 234, "Vijayawada": 234,
    "Visakhapatnam": 234, "Warangal": 228,
}

def make_sales(total, n):
    if n == 1:
        return np.array([round(total, 2)])
    raw = rng.lognormal(mean=0.0, sigma=0.55, size=n)
    vals = raw / raw.sum() * total
    vals = np.round(vals, 2)
    vals[-1] = round(total - vals[:-1].sum(), 2)
    return vals

rows = []
order_num = 1
for region in ACTIVE:
    n = COUNTS[region]
    # Distribute each region's rows across Apr/May/Jun, while preserving
    # exactly the verified regional-month sales totals.
    month_counts = [n // 3, n // 3, n - 2*(n // 3)]
    for month_idx, count in enumerate(month_counts):
        sales = make_sales(TARGETS[region][month_idx], count)
        for s in sales:
            category = CATEGORIES[(order_num + month_idx) % len(CATEGORIES)]
            product = PRODUCTS[category][order_num % len(PRODUCTS[category])]
            month = month_idx + 4
            day = int(rng.integers(1, 28))
            date = f"2026-{month:02d}-{day:02d}"
            profit = round(float(s) * MARGINS[category], 2)
            rows.append([
                f"ORD{order_num:05d}", date, region, product, category,
                float(s), profit, "Telangana" if region != "Bengaluru" else "Karnataka"
            ])
            order_num += 1

raw_clean = pd.DataFrame(rows, columns=[
    "order_id", "order_date", "region", "product", "category",
    "sales_inr", "profit_inr", "state"
])

# Inject deterministic missing values into analytical rows.
# Category can be recovered from product; profit is imputed from category margin.
raw_clean.loc[raw_clean.index[:48], "category"] = np.nan
raw_clean.loc[raw_clean.index[48:142], "profit_inr"] = np.nan

# Inject 59 exact duplicate rows.
dupes = raw_clean.iloc[:59].copy()
raw = pd.concat([raw_clean, dupes], ignore_index=True)

master = pd.DataFrame({
    "region": REGIONS,
    "state": ["Telangana"]*8 + ["Karnataka", "Andhra Pradesh"],
    "is_active": [1]*9 + [0],
    "region_code": ["HYD","WAR","VJA","VIZ","GNT","NEL","TPT","KNR","BLR","KUR"],
})

raw.to_csv(OUT / "pharmeasy_orders_raw.csv", index=False)
master.to_csv(OUT / "regions_master.csv", index=False)

print(f"Generated raw rows: {len(raw)}")
print(f"Generated master rows: {len(master)}")
print("Seed:", SEED)
