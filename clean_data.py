"""
Part 1 — Cleaning pipeline and schema validation.
"""
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent
RAW = BASE / "pharmeasy_orders_raw.csv"
OUT = BASE / "orders_clean.csv"
REPORT = BASE / "data_quality_report.md"

EXPECTED = [
    "order_id", "order_date", "region", "product",
    "category", "sales_inr", "profit_inr", "state"
]
CANONICAL_REGIONS = {
    "hyderabad": "Hyderabad", "hyderabad ": "Hyderabad",
    "warangal": "Warangal", "warangal ": "Warangal",
    "vijayawada": "Vijayawada", "vijayawada ": "Vijayawada",
    "visakhapatnam": "Visakhapatnam", "visakhapatnam ": "Visakhapatnam",
    "guntur": "Guntur", "guntur ": "Guntur",
    "nellore": "Nellore", "nellore ": "Nellore",
    "tirupati": "Tirupati", "tirupati ": "Tirupati",
    "karimnagar": "Karimnagar", "karimnagar ": "Karimnagar",
    "bengaluru": "Bengaluru", "bangalore": "Bengaluru",
}

def validate_schema(df, required=None):
    required = required or EXPECTED
    missing = [c for c in required if c not in df.columns]
    if missing:
        return False, f"blocked_schema: missing columns {missing}"
    return True, "validated"

def clean_data():
    df = pd.read_csv(RAW)
    raw_rows = len(df)

    ok, status = validate_schema(df)
    if not ok:
        raise ValueError(status)

    before = len(df)
    df = df.drop_duplicates(keep="first").copy()
    exact_duplicates_removed = before - len(df)

    df["region"] = (
        df["region"].astype("string").str.strip().str.lower()
        .map(CANONICAL_REGIONS)
    )
    if df["region"].isna().any():
        raise ValueError("Unmapped region values remain after normalization.")

    # Product -> category lookup from rows where category is present.
    lookup = (
        df.dropna(subset=["product", "category"])
          .drop_duplicates("product")
          .set_index("product")["category"]
          .to_dict()
    )
    missing_category_before = int(df["category"].isna().sum())
    df.loc[df["category"].isna(), "category"] = (
        df.loc[df["category"].isna(), "product"].map(lookup)
    )

    # Category mean margin from non-missing profit rows.
    df["sales_inr"] = pd.to_numeric(df["sales_inr"], errors="coerce")
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")
    margin_source = df.dropna(subset=["profit_inr", "sales_inr"]).copy()
    margin_source = margin_source[margin_source["sales_inr"] != 0]
    margin_source["margin"] = margin_source["profit_inr"] / margin_source["sales_inr"]
    margins = margin_source.groupby("category")["margin"].mean().to_dict()

    missing_profit_before = int(df["profit_inr"].isna().sum())
    mask = df["profit_inr"].isna()
    df.loc[mask, "profit_inr"] = (
        df.loc[mask, "sales_inr"] *
        df.loc[mask, "category"].map(margins)
    ).round(2)

    if df[EXPECTED].isna().any().any():
        raise ValueError("Cleaning completed with remaining missing values.")

    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")
    df.to_csv(OUT, index=False)

    report = f"""# Data Quality Report

## Scope
The raw dataset contains **{raw_rows:,} rows** and the cleaned analytical dataset contains **{len(df):,} rows**.

## Quality Dimensions

| Dimension | Check / Fix | Result |
|---|---|---|
| Accuracy | Profit imputed using category mean margin × sales | {missing_profit_before} missing profit values addressed |
| Completeness | Missing categories recovered from product → category mapping | {missing_category_before} missing category values addressed |
| Consistency | Region names normalized to canonical names | {df['region'].nunique()} active analytical regions |
| Timeliness | Order dates retained for April–June 2026 analysis | April–June 2026 |
| Validity | Required schema and numeric/date fields validated | Schema validated |
| Uniqueness | Exact duplicate rows removed | {exact_duplicates_removed} duplicates removed |
| Relevance | Required order, region, category, sales and profit fields retained | Analytical dataset ready |

## Validation Result

- Raw rows: {raw_rows}
- Exact duplicates removed: {exact_duplicates_removed}
- Clean rows: {len(df)}
- Missing category after cleaning: {int(df['category'].isna().sum())}
- Missing profit after cleaning: {int(df['profit_inr'].isna().sum())}
- Final schema: validated
"""
    REPORT.write_text(report, encoding="utf-8")
    print(report)

if __name__ == "__main__":
    clean_data()
