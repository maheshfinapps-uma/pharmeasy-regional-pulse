from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="PharmaEasy Regional Pulse",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parent / "orders_clean.csv"

@st.cache_data
def load_orders():
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "order_id", "order_date", "region", "product",
        "category", "sales_inr", "profit_inr", "state"
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["sales_inr"] = pd.to_numeric(df["sales_inr"], errors="coerce")
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")
    df = df.dropna(
        subset=["order_id", "order_date", "region", "category", "sales_inr", "profit_inr"]
    ).copy()
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df

df = load_orders()

MONTH_ORDER = ["2026-04", "2026-05", "2026-06"]
MONTH_LABELS = {
    "2026-04": "April 2026",
    "2026-05": "May 2026",
    "2026-06": "June 2026",
}
ALL_REGIONS = ["All Regions"] + sorted(df["region"].dropna().unique().tolist())

st.title("📊 PharmaEasy Regional Pulse")
st.caption("Regional sales, profitability and order-performance dashboard | April–June 2026")

selected_region = st.selectbox("Select Region", ALL_REGIONS, index=0)

if selected_region == "All Regions":
    filtered_df = df.copy()
else:
    filtered_df = df[df["region"] == selected_region].copy()

total_sales = filtered_df["sales_inr"].sum()
total_profit = filtered_df["profit_inr"].sum()
distinct_orders = filtered_df["order_id"].nunique()

# ============================================================
# Task 4.2 — Embedded Executive Summary
# ============================================================
st.subheader("Executive Summary")

if selected_region == "All Regions":
    summary = (
        f"The dashboard covers {distinct_orders:,} distinct orders, generating "
        f"total sales of ₹{total_sales:,.2f} and total profit of ₹{total_profit:,.2f} "
        f"across the nine active regions for April–June 2026. "
        f"Guntur recorded the largest-magnitude flagged movement, increasing from "
        f"₹62,442.27 in April to ₹138,738.93 in May (+122.19%) before declining to "
        f"₹99,745.18 in June (-28.11%). "
        f"At the regional level, Hyderabad reached ₹294,088.56 in June, while the "
        f"category view shows the sales mix within the selected scope. "
        f"The immediate action is to investigate the Guntur order- and category-level "
        f"drivers; use the regional trend, category breakdown, and detail table below "
        f"to validate the movement."
    )
else:
    region_month = (
        filtered_df.groupby("month", as_index=False)["sales_inr"]
        .sum()
        .set_index("month")["sales_inr"]
    )
    april_sales = float(region_month.get("2026-04", 0))
    may_sales = float(region_month.get("2026-05", 0))
    june_sales = float(region_month.get("2026-06", 0))
    apr_may_change = ((may_sales - april_sales) / april_sales * 100) if april_sales else 0.0
    may_june_change = ((june_sales - may_sales) / may_sales * 100) if may_sales else 0.0

    summary = (
        f"The selected {selected_region} scope contains {distinct_orders:,} distinct "
        f"orders, generating total sales of ₹{total_sales:,.2f} and total profit of "
        f"₹{total_profit:,.2f} for April–June 2026. "
        f"Sales moved from ₹{april_sales:,.2f} in April to ₹{may_sales:,.2f} in May "
        f"({apr_may_change:+.2f}%), then to ₹{june_sales:,.2f} in June "
        f"({may_june_change:+.2f}%). "
        f"The category view shows the sales mix for {selected_region}, while the "
        f"regional trend and detail table provide supporting evidence. "
        f"The next action is to review the contributing orders and categories before "
        f"making an operational decision."
    )

st.info(summary)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sales (INR)", f"₹{total_sales:,.2f}")
with col2:
    st.metric("Total Profit (INR)", f"₹{total_profit:,.2f}")
with col3:
    st.metric("Distinct Orders", f"{distinct_orders:,}")

# ============================================================
# Category Level
# ============================================================
st.subheader("Category Analysis")

category_month = st.selectbox(
    "Select Month for Category Breakdown",
    MONTH_ORDER,
    format_func=lambda x: MONTH_LABELS.get(x, x),
)

category_df = (
    filtered_df[filtered_df["month"] == category_month]
    .groupby("category", as_index=False)["sales_inr"]
    .sum()
    .sort_values("sales_inr", ascending=False)
)

if not category_df.empty:
    fig_donut = px.pie(
        category_df,
        names="category",
        values="sales_inr",
        hole=0.45,
        title=f"Which categories drive sales in {MONTH_LABELS.get(category_month, category_month)}?",
    )
    fig_donut.update_traces(textposition="inside", textinfo="percent+label")
    fig_donut.update_layout(
        legend_title_text="Category",
        margin=dict(t=70, l=20, r=20, b=20),
    )
    st.plotly_chart(fig_donut, use_container_width=True)
else:
    st.warning("No category data is available for the selected month and region.")

# ============================================================
# Overview — Regional Trend
# ============================================================
st.subheader("Regional Sales Trend")

trend_df = (
    filtered_df[filtered_df["month"].isin(MONTH_ORDER)]
    .groupby(["month", "region"], as_index=False)["sales_inr"]
    .sum()
)
trend_df["Month"] = trend_df["month"].map(MONTH_LABELS)

fig_line = px.line(
    trend_df,
    x="Month",
    y="sales_inr",
    color="region",
    markers=True,
    category_orders={"Month": [MONTH_LABELS[m] for m in MONTH_ORDER]},
    title="How did regional sales change from April to June?",
    labels={"Month": "Month", "sales_inr": "Sales (INR)", "region": "Region"},
)
for trace in fig_line.data:
    if trace.name == "Guntur":
        trace.update(line=dict(width=4))
    else:
        trace.update(line=dict(width=2))
fig_line.update_yaxes(rangemode="tozero")
fig_line.update_layout(hovermode="x unified", margin=dict(t=70, l=20, r=20, b=20))
st.plotly_chart(fig_line, use_container_width=True)

# ============================================================
# Overview — Regional Comparison
# ============================================================
st.subheader("Regional Sales Comparison")

region_sales = (
    filtered_df.groupby("region", as_index=False)["sales_inr"]
    .sum()
    .sort_values("sales_inr", ascending=True)
)

fig_bar = px.bar(
    region_sales,
    x="sales_inr",
    y="region",
    orientation="h",
    title="Which regions generate the most total sales?",
    labels={"sales_inr": "Total Sales (INR)", "region": "Region"},
)
fig_bar.update_xaxes(rangemode="tozero")
fig_bar.update_layout(margin=dict(t=70, l=20, r=20, b=20))
st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================
# Detail Level
# ============================================================
st.subheader("Regional / Monthly Detail")

detail_df = (
    filtered_df[filtered_df["month"].isin(MONTH_ORDER)]
    .groupby(["region", "month"], as_index=False)
    .agg(
        sales_inr=("sales_inr", "sum"),
        profit_inr=("profit_inr", "sum"),
        distinct_orders=("order_id", "nunique"),
    )
)
detail_df["Month"] = detail_df["month"].map(MONTH_LABELS)
detail_df = detail_df[
    ["region", "Month", "sales_inr", "profit_inr", "distinct_orders"]
].sort_values(["region", "Month"])
detail_df = detail_df.rename(
    columns={
        "region": "Region",
        "sales_inr": "Sales (INR)",
        "profit_inr": "Profit (INR)",
        "distinct_orders": "Distinct Orders",
    }
)
st.dataframe(detail_df, use_container_width=True, hide_index=True)

st.caption(
    "Methodology: metrics are calculated from orders_clean.csv. "
    "Order-count KPIs use distinct order_id values. "
    "The 8% monthly movement threshold is an operational alert rule, "
    "not a statistical significance test."
)
