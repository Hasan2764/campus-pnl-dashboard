# =========================================================
# STREAMLIT PROFIT & LOSS DASHBOARD (PRODUCTION READY)
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
def generate_pdf(df, income_total, expense_total, profit):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Usman Public School System", styles['Title']))
    elements.append(Paragraph("Profit & Loss Dashboard Report", styles['Heading2']))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Total Income: {income_total:,.0f}", styles['Normal']))
    elements.append(Paragraph(f"Total Expense: {expense_total:,.0f}", styles['Normal']))
    elements.append(Paragraph(f"Profit/Loss: {profit:,.0f}", styles['Normal']))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Total Records: {len(df)}", styles['Normal']))
    elements.append(Paragraph(f"Total Amount: {df['Amount'].sum():,.0f}", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)

    return buffer
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
    <h1 style='text-align:center;'>Usman Public School System</h1>
    <h3 style='text-align:center;'>Profit & Loss Dashboard</h3>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

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

df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
df["Month"] = df["Month"].dt.strftime("%b-%y")

# ---------------------------------------------------------
# FILTERS (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

campus_list = df["Campus"].dropna().unique().tolist()
month_list = df["Month"].dropna().unique().tolist()

campus_filter = st.sidebar.multiselect("Campus", campus_list, default=campus_list)
month_filter = st.sidebar.multiselect("Month", month_list, default=month_list)

filtered_df = df[
    (df["Campus"].isin(campus_filter)) &
    (df["Month"].isin(month_filter))
]

# ---------------------------------------------------------
# PIVOT CALCULATIONS
# ---------------------------------------------------------
income_total = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
expense_total = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
profit = income_total - expense_total

# Monthly trend

# MoM Change

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
    pie_df = pd.DataFrame({
        "Type": ["Income", "Expense"],
        "Amount": [income_total, expense_total]
    })

    fig2 = px.pie(
        pie_df,
        names="Type",
        values="Amount",
        title="Income vs Expense (%)"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# TABLE VIEW
# ---------------------------------------------------------
st.subheader("📋 Processed Data View")
display_df = filtered_df.reset_index(drop=True)
display_df.index = display_df.index + 1
st.dataframe(display_df)

# ---------------------------------------------------------
# EXPORT FUNCTIONS
# ---------------------------------------------------------
def convert_excel(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        # Full filtered data
        df.to_excel(writer, index=False, sheet_name="Data")

        # KPI Summary
        summary = pd.DataFrame({
            "Metric": ["Income", "Expense", "Profit"],
            "Value": [income_total, expense_total, profit]
        })

        summary.to_excel(
            writer,
            index=False,
            sheet_name="Summary"
        )

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
    pdf_data = generate_pdf(
        filtered_df,
        income_total,
        expense_total,
        profit
    )

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name="campus_pnl_report.pdf",
        mime="application/pdf"
    )

    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    elements.append(Paragraph("Usman Public School System", styles["Title"]))
    elements.append(Paragraph("Profit & Loss Dashboard Report", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # KPIs
    elements.append(Paragraph(f"Total Income: {income_total:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Total Expense: {expense_total:,.0f}", styles["Normal"]))
    elements.append(Paragraph(f"Profit/Loss: {profit:,.0f}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # TABLE PREVIEW (first 20 rows only)
    elements.append(Paragraph("Data Preview (Top 20 Rows)", styles["Heading3"]))

    preview_df = df.head(20)
    table_data = [preview_df.columns.tolist()] + preview_df.values.tolist()

    from reportlab.platypus import Table
    table = Table(table_data)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_data,
    file_name="campus_pnl_report.pdf",
    mime="application/pdf"
)

# ---------------------------------------------------------
# REQUIREMENTS.TXT
# ---------------------------------------------------------
