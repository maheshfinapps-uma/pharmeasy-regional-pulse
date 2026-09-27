
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PharmaEasy Regional Pulse",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_PATH = Path("orders_clean.csv")

FLAGGED_REGION = "Guntur"

MONTH_ORDER = [
    "2026-04",
    "2026-05",
    "2026-06"
]

MONTH_LABELS = {
    "2026-04": "April 2026",
    "2026-05": "May 2026",
    "2026-06": "June 2026"
}


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Required file not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "order_id",
        "order_date",
        "region",
        "product",
        "category",
        "sales_inr",
        "profit_inr",
        "quantity"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    if df["order_date"].isna().any():
        raise ValueError(
            "Invalid order_date values found."
        )

    df["month"] = df["order_date"].dt.strftime("%Y-%m")

    df["sales_inr"] = pd.to_numeric(
        df["sales_inr"],
        errors="coerce"
    )

    df["profit_inr"] = pd.to_numeric(
        df["profit_inr"],
        errors="coerce"
    )

    return df


orders = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("📊 PharmaEasy Regional Pulse")

st.caption(
    "Regional sales, profit and order performance — "
    "April to June 2026"
)


# ============================================================
# REGION FILTER
# ============================================================

st.sidebar.header("Dashboard Filters")

regions = sorted(
    orders["region"].dropna().unique().tolist()
)

region_options = ["All Regions"] + regions

selected_region = st.sidebar.selectbox(
    "Select region",
    region_options
)


# ============================================================
# APPLY REGION FILTER
# ============================================================

if selected_region == "All Regions":

    filtered_orders = orders.copy()

else:

    filtered_orders = orders[
        orders["region"] == selected_region
    ].copy()


# ============================================================
# MONTH FILTER FOR CATEGORY VIEW
# ============================================================

month_options = [
    "All Months",
    "2026-04",
    "2026-05",
    "2026-06"
]

selected_month = st.sidebar.selectbox(
    "Category month",
    month_options,
    format_func=lambda x:
        "All Months"
        if x == "All Months"
        else MONTH_LABELS[x]
)


if selected_month == "All Months":

    category_orders = filtered_orders.copy()

else:

    category_orders = filtered_orders[
        filtered_orders["month"] == selected_month
    ].copy()


# ============================================================
# TASK 4.2 — EXECUTIVE SUMMARY
# ============================================================

st.header("Executive Summary")

st.info(
    "Across the selected scope, the dashboard reports total sales, "
    "total profit and distinct order activity for April–June 2026. "
    "Guntur sales increased from ₹62,442.27 in April to ₹138,738.93 "
    "in May, a +122.19% month-over-month movement, before declining "
    "to ₹99,745.18 in June. "
    "The category view shows the sales mix behind the selected scope, "
    "while the regional trend and detail table support investigation "
    "of the underlying movement."
)


# ============================================================
# LEVEL 1 — OVERVIEW
# ============================================================

st.header("1. Overview")

total_sales = filtered_orders["sales_inr"].sum()

total_profit = filtered_orders["profit_inr"].sum()

# IMPORTANT:
# Distinct order_id count.
# This is NOT len(filtered_orders).
distinct_orders = filtered_orders["order_id"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Sales (INR)",
        f"₹{total_sales:,.2f}"
    )

with col2:
    st.metric(
        "Total Profit (INR)",
        f"₹{total_profit:,.2f}"
    )

with col3:
    st.metric(
        "Distinct Orders",
        f"{distinct_orders:,}"
    )


# ============================================================
# LEVEL 2 — CATEGORY
# ============================================================

st.header("2. Category Breakdown")

category_summary = (
    category_orders
    .groupby("category", as_index=False)
    .agg(
        sales_inr=("sales_inr", "sum"),
        profit_inr=("profit_inr", "sum"),
        distinct_orders=("order_id", "nunique")
    )
    .sort_values(
        "sales_inr",
        ascending=False
    )
)

# ------------------------------------------------------------
# DONUT CHART
# ------------------------------------------------------------

donut = go.Figure()

donut.add_trace(
    go.Pie(
        labels=category_summary["category"],
        values=category_summary["sales_inr"],
        hole=0.50,
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales (INR): ₹%{value:,.2f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )
)

donut.update_layout(
    title="Which categories contribute to sales?",
    height=500,
    legend_title="Medicine Category",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=20
    )
)

st.plotly_chart(
    donut,
    use_container_width=True
)


# ------------------------------------------------------------
# CATEGORY TABLE
# ------------------------------------------------------------

category_display = category_summary.copy()

category_display["sales_inr"] = (
    category_display["sales_inr"].round(2)
)

category_display["profit_inr"] = (
    category_display["profit_inr"].round(2)
)

st.dataframe(
    category_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TREND / LINE CHART
# ============================================================

st.header("3. Monthly Sales Trend")

trend = (
    filtered_orders
    .groupby(
        ["month", "region"],
        as_index=False
    )["sales_inr"]
    .sum()
)

trend["month_sort"] = trend["month"].map({
    "2026-04": 1,
    "2026-05": 2,
    "2026-06": 3
})

trend["month_label"] = trend["month"].map(
    MONTH_LABELS
)

trend = trend.sort_values(
    ["month_sort", "region"]
)


line_chart = go.Figure()

for region in sorted(trend["region"].unique()):

    region_data = trend[
        trend["region"] == region
    ].sort_values("month_sort")

    # Highlight only the flagged Guntur series.
    if region == FLAGGED_REGION:

        line_color = "#D62728"
        line_width = 4

    else:

        line_color = "#7F8C8D"
        line_width = 2

    line_chart.add_trace(
        go.Scatter(
            x=region_data["month_label"],
            y=region_data["sales_inr"],
            mode="lines+markers",
            name=region,
            line=dict(
                color=line_color,
                width=line_width
            ),
            marker=dict(
                size=7
            ),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Month: %{x}<br>"
                "Sales (INR): ₹%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )


line_chart.update_layout(
    title="How did regional sales change from April to June?",
    xaxis_title="Month",
    yaxis_title="Sales (INR)",
    height=550,
    hovermode="x unified",
    legend_title="Region",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=20
    )
)

# Zero baseline — no truncated quantitative axis.
line_chart.update_yaxes(
    rangemode="tozero"
)

st.plotly_chart(
    line_chart,
    use_container_width=True
)


# ============================================================
# REGIONAL COMPARISON / BAR CHART
# ============================================================

st.header("4. Regional Comparison")

region_summary = (
    orders
    .groupby("region", as_index=False)
    .agg(
        sales_inr=("sales_inr", "sum"),
        distinct_orders=("order_id", "nunique")
    )
    .sort_values(
        "sales_inr",
        ascending=True
    )
)

bar_colors = [
    "#D62728"
    if region == FLAGGED_REGION
    else "#7F8C8D"
    for region in region_summary["region"]
]


bar_chart = go.Figure()

bar_chart.add_trace(
    go.Bar(
        x=region_summary["sales_inr"],
        y=region_summary["region"],
        orientation="h",
        marker_color=bar_colors,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Total Sales (INR): ₹%{x:,.2f}"
            "<extra></extra>"
        )
    )
)

bar_chart.update_layout(
    title="Which regions generate the most total sales?",
    xaxis_title="Total Sales (INR)",
    yaxis_title="Region",
    height=550,
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=20
    )
)

# Zero baseline — no truncation.
bar_chart.update_xaxes(
    rangemode="tozero"
)

st.plotly_chart(
    bar_chart,
    use_container_width=True
)


# ============================================================
# LEVEL 3 — DETAIL
# ============================================================

st.header("5. Regional × Monthly Detail")

detail = (
    filtered_orders
    .groupby(
        ["region", "month"],
        as_index=False
    )
    .agg(
        sales_inr=("sales_inr", "sum"),
        profit_inr=("profit_inr", "sum"),
        distinct_orders=("order_id", "nunique")
    )
)

detail["month"] = detail["month"].map(
    MONTH_LABELS
)

detail = detail.sort_values(
    ["region", "month"]
)

detail["sales_inr"] = detail["sales_inr"].round(2)
detail["profit_inr"] = detail["profit_inr"].round(2)

st.dataframe(
    detail,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# METHODOLOGY
# ============================================================

st.divider()

st.caption(
    "Methodology: sales and profit are aggregated from the cleaned "
    "order dataset. Order counts use distinct order_id values. "
    "The Guntur series is highlighted because its April→May "
    "movement of +122.19% exceeded the Part 2 operational alert "
    "threshold."
)
