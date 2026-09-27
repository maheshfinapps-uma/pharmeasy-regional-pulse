from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PharmaEasy Regional Pulse — Streamlit Dashboard
# ============================================================

st.set_page_config(
    page_title="PharmaEasy Regional Pulse",
    page_icon="📊",
    layout="wide",
)

# Streamlit Cloud and local execution:
# orders_clean.csv must be in the same folder as app.py.
DATA_PATH = Path(__file__).resolve().parent / "orders_clean.csv"


# ============================================================
# DATA LOADING AND VALIDATION
# ============================================================

@st.cache_data
def load_orders():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"orders_clean.csv was not found beside app.py. "
            f"Expected file: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Only require fields actually used by this dashboard.
    # product and state are intentionally NOT required.
    required_columns = [
        "order_id",
        "order_date",
        "region",
        "category",
        "sales_inr",
        "profit_inr",
    ]

    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns in orders_clean.csv: {missing}. "
            f"Available columns are: {list(df.columns)}"
        )

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["sales_inr"] = pd.to_numeric(df["sales_inr"], errors="coerce")
    df["profit_inr"] = pd.to_numeric(df["profit_inr"], errors="coerce")

    df = df.dropna(
        subset=[
            "order_id",
            "order_date",
            "region",
            "category",
            "sales_inr",
            "profit_inr",
        ]
    ).copy()

    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    return df


df = load_orders()


# ============================================================
# CONSTANTS
# ============================================================

MONTH_ORDER = [
    "2026-04",
    "2026-05",
    "2026-06",
]

MONTH_LABELS = {
    "2026-04": "April 2026",
    "2026-05": "May 2026",
    "2026-06": "June 2026",
}

ALL_REGIONS = [
    "All Regions"
] + sorted(df["region"].dropna().unique().tolist())


# ============================================================
# HEADER
# ============================================================

st.title("📊 PharmaEasy Regional Pulse")

st.caption(
    "Regional sales, profitability and order-performance dashboard | "
    "April–June 2026"
)


# ============================================================
# REGION FILTER
# ============================================================

selected_region = st.selectbox(
    "Select Region",
    ALL_REGIONS,
    index=0,
)

if selected_region == "All Regions":
    filtered_df = df.copy()
else:
    filtered_df = df[df["region"] == selected_region].copy()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_df["sales_inr"].sum()
total_profit = filtered_df["profit_inr"].sum()

# IMPORTANT:
# Order count uses DISTINCT order_id, not raw row count.
distinct_orders = filtered_df["order_id"].nunique()


# ============================================================
# TASK 4.2 — EMBEDDED EXECUTIVE SUMMARY
# ============================================================

st.subheader("Executive Summary")

if selected_region == "All Regions":

    # Verified Part 2 / Part 3 figures for the complete active-region scope.
    summary = (
        f"The dashboard covers {distinct_orders:,} distinct orders, generating "
        f"total sales of ₹{total_sales:,.2f} and total profit of "
        f"₹{total_profit:,.2f} across the nine active regions for April–June "
        f"2026. Guntur recorded the largest-magnitude flagged movement, "
        f"increasing from ₹62,442.27 in April to ₹138,738.93 in May "
        f"(+122.19%) before declining to ₹99,745.18 in June (-28.11%). "
        f"At the regional level, Hyderabad reached ₹294,088.56 in June, "
        f"while the category view shows the sales mix within the selected "
        f"scope. The immediate action is to investigate the Guntur "
        f"order- and category-level drivers; use the regional trend, "
        f"category breakdown, and detail table below to validate the movement."
    )

else:

    # Dynamically calculate the selected-region monthly movement.
    region_month = (
        filtered_df.groupby("month", as_index=False)["sales_inr"]
        .sum()
        .set_index("month")["sales_inr"]
    )

    april_sales = float(region_month.get("2026-04", 0))
    may_sales = float(region_month.get("2026-05", 0))
    june_sales = float(region_month.get("2026-06", 0))

    if april_sales != 0:
        apr_may_change = (
            (may_sales - april_sales) / april_sales
        ) * 100
    else:
        apr_may_change = 0.0

    if may_sales != 0:
        may_june_change = (
            (june_sales - may_sales) / may_sales
        ) * 100
    else:
        may_june_change = 0.0

    summary = (
        f"The selected {selected_region} scope contains {distinct_orders:,} "
        f"distinct orders, generating total sales of ₹{total_sales:,.2f} "
        f"and total profit of ₹{total_profit:,.2f} for April–June 2026. "
        f"Sales moved from ₹{april_sales:,.2f} in April to "
        f"₹{may_sales:,.2f} in May ({apr_may_change:+.2f}%), then to "
        f"₹{june_sales:,.2f} in June ({may_june_change:+.2f}%). "
        f"The category view shows the sales mix for {selected_region}, "
        f"while the regional trend and detail table provide supporting "
        f"evidence. The next action is to review the contributing orders "
        f"and categories before making an operational decision."
    )

st.info(summary)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Sales (INR)",
        f"₹{total_sales:,.2f}",
    )

with col2:
    st.metric(
        "Total Profit (INR)",
        f"₹{total_profit:,.2f}",
    )

with col3:
    st.metric(
        "Distinct Orders",
        f"{distinct_orders:,}",
    )


# ============================================================
# CATEGORY LEVEL
# ============================================================

st.subheader("Category Analysis")

category_month = st.selectbox(
    "Select Month for Category Breakdown",
    MONTH_ORDER,
    format_func=lambda x: MONTH_LABELS.get(x, x),
)

category_df = (
    filtered_df[
        filtered_df["month"].isin(MONTH_ORDER)
        & (filtered_df["month"] == category_month)
    ]
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
        title=(
            f"Which categories drive sales in "
            f"{MONTH_LABELS.get(category_month, category_month)}?"
        ),
    )

    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent+label",
    )

    fig_donut.update_layout(
        legend_title_text="Category",
        margin=dict(
            t=70,
            l=20,
            r=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_donut,
        use_container_width=True,
    )

else:
    st.warning(
        "No category data is available for the selected month and region."
    )


# ============================================================
# OVERVIEW LEVEL — REGIONAL SALES TREND
# ============================================================

st.subheader("Regional Sales Trend")

trend_df = (
    filtered_df[
        filtered_df["month"].isin(MONTH_ORDER)
    ]
    .groupby(
        ["month", "region"],
        as_index=False,
    )["sales_inr"]
    .sum()
)

trend_df["Month"] = trend_df["month"].map(MONTH_LABELS)

fig_line = px.line(
    trend_df,
    x="Month",
    y="sales_inr",
    color="region",
    markers=True,
    category_orders={
        "Month": [
            MONTH_LABELS[m]
            for m in MONTH_ORDER
        ]
    },
    title="How did regional sales change from April to June?",
    labels={
        "Month": "Month",
        "sales_inr": "Sales (INR)",
        "region": "Region",
    },
)

# Guntur is the flagged region highlighted in the assessment narrative.
# Other series retain the default Plotly treatment.
for trace in fig_line.data:
    if trace.name == "Guntur":
        trace.update(
            line=dict(width=4),
            marker=dict(size=8),
        )
    else:
        trace.update(
            line=dict(width=2),
        )

fig_line.update_yaxes(
    rangemode="tozero",
)

fig_line.update_layout(
    hovermode="x unified",
    margin=dict(
        t=70,
        l=20,
        r=20,
        b=20,
    ),
)

st.plotly_chart(
    fig_line,
    use_container_width=True,
)


# ============================================================
# OVERVIEW LEVEL — REGIONAL COMPARISON
# ============================================================

st.subheader("Regional Sales Comparison")

region_sales = (
    filtered_df
    .groupby("region", as_index=False)["sales_inr"]
    .sum()
    .sort_values("sales_inr", ascending=True)
)

fig_bar = px.bar(
    region_sales,
    x="sales_inr",
    y="region",
    orientation="h",
    title="Which regions generate the most total sales?",
    labels={
        "sales_inr": "Total Sales (INR)",
        "region": "Region",
    },
)

fig_bar.update_xaxes(
    rangemode="tozero",
)

fig_bar.update_layout(
    margin=dict(
        t=70,
        l=20,
        r=20,
        b=20,
    ),
)

st.plotly_chart(
    fig_bar,
    use_container_width=True,
)


# ============================================================
# DETAIL LEVEL
# ============================================================

st.subheader("Regional / Monthly Detail")

detail_df = (
    filtered_df[
        filtered_df["month"].isin(MONTH_ORDER)
    ]
    .groupby(
        ["region", "month"],
        as_index=False,
    )
    .agg(
        sales_inr=("sales_inr", "sum"),
        profit_inr=("profit_inr", "sum"),
        distinct_orders=("order_id", "nunique"),
    )
)

detail_df["Month"] = detail_df["month"].map(MONTH_LABELS)

detail_df = detail_df[
    [
        "region",
        "Month",
        "sales_inr",
        "profit_inr",
        "distinct_orders",
    ]
].sort_values(
    ["region", "Month"]
)

detail_df = detail_df.rename(
    columns={
        "region": "Region",
        "sales_inr": "Sales (INR)",
        "profit_inr": "Profit (INR)",
        "distinct_orders": "Distinct Orders",
    }
)

st.dataframe(
    detail_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# METHODOLOGY
# ============================================================

st.caption(
    "Methodology: metrics are calculated from orders_clean.csv. "
    "Order-count KPIs use distinct order_id values. "
    "The 8% monthly movement threshold is an operational alert rule, "
    "not a statistical significance test."
)
