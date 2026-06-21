# =========================================================
# STREAMLIT PROFIT & LOSS DASHBOARD (PRODUCTION READY)
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# ---------------------------------------------------------
# PAGE CONFIG + THEME SUPPORT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Campus P&L Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .main { background-color: #0e1117; }
        h1, h2, h3 { color: #ffffff; }
        .stMetric { background-color: #1c1f26; padding: 10px; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("🏫 Campus-wise Profit & Loss Dashboard")

# ---------------------------------------------------------
# FILE UPLOADS
# ---------------------------------------------------------
st.sidebar.header("📂 Upload Data Files")

income_file = st.sidebar.file_uploader("Upload Income File", type=["csv", "xlsx"])
expense_file = st.sidebar.file_uploader("Upload Expense File", type=["csv", "xlsx"])

# ---------------------------------------------------------
# DATA LOADING FUNCTION
# ---------------------------------------------------------
def load_file(file):
    if file is None:
        return pd.DataFrame()
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

income_df = load_file(income_file)
expense_df = load_file(expense_file)

# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------
if income_df.empty or expense_df.empty:
    st.warning("Please upload both Income and Expense files to continue.")
    st.stop()

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------
def clean_data(df, data_type):
    df = df.copy()
    df.columns = [c.strip().title() for c in df.columns]
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Type"] = data_type
    return df

income_df = clean_data(income_df, "Income")
expense_df = clean_data(expense_df, "Expense")

df = pd.concat([income_df, expense_df], ignore_index=True)

# ---------------------------------------------------------
# FILTERS (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

campus_list = df["Campus"].dropna().unique().tolist()
month_list = df["Month"].dropna().unique().tolist()
category_list = df["Account"].dropna().unique().tolist()

campus_filter = st.sidebar.multiselect("Campus", campus_list, default=campus_list)
month_filter = st.sidebar.multiselect("Month", month_list, default=month_list)
category_filter = st.sidebar.multiselect("Category", category_list, default=category_list)

filtered_df = df[
    (df["Campus"].isin(campus_filter)) &
    (df["Month"].isin(month_filter)) &
    (df["Account"].isin(category_filter))
]

# ---------------------------------------------------------
# PIVOT CALCULATIONS
# ---------------------------------------------------------
income_total = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
expense_total = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
profit = income_total - expense_total

# Monthly trend
trend = filtered_df.groupby(["Month", "Type"])["Amount"].sum().reset_index()
trend_pivot = trend.pivot(index="Month", columns="Type", values="Amount").fillna(0)
trend_pivot["Profit"] = trend_pivot.get("Income", 0) - trend_pivot.get("Expense", 0)

# MoM Change
trend_pivot["MoM_Profit_%"] = trend_pivot["Profit"].pct_change().fillna(0) * 100

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"{income_total:,.0f}")
col2.metric("Total Expense", f"{expense_total:,.0f}")
col3.metric("Profit / Loss", f"{profit:,.0f}")

# ---------------------------------------------------------
# CHARTS
# ---------------------------------------------------------
st.subheader("📈 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    expense_chart = filtered_df[filtered_df["Type"] == "Expense"]
    fig1 = px.bar(
        expense_chart,
        x="Account",
        y="Amount",
        color="Campus",
        title="Expense Breakdown by Category"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(
        trend_pivot.reset_index(),
        x="Month",
        y=["Income", "Expense", "Profit"],
        title="Monthly Trend (Income vs Expense vs Profit)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# TABLE VIEW
# ---------------------------------------------------------
st.subheader("📋 Processed Data View")
st.dataframe(filtered_df, use_container_width=True)

# ---------------------------------------------------------
# EXPORT FUNCTIONS
# ---------------------------------------------------------
def convert_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

st.subheader("📤 Export Options")

col1, col2 = st.columns(2)

with col1:
    excel_data = convert_excel(filtered_df)
    st.download_button(
        "⬇ Download Excel Report",
        data=excel_data,
        file_name="campus_pnl_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download CSV Report",
        data=csv_data,
        file_name="campus_pnl_report.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# REQUIREMENTS.TXT
# ---------------------------------------------------------
st.markdown("""
---
### requirements.txt


streamlit
pandas
numpy
plotly
xlsxwriter

""")
