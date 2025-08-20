import streamlit as st
import pandas as pd
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(page_title="FinanceHub Dashboard", layout="wide")

st.title("📊 FinanceHub Dashboard")

# ---- Sidebar Filters ----
st.sidebar.header("Filters & Controls")
category = st.sidebar.selectbox("Category", ["Food", "Drinks", "Electronics"])
company = st.sidebar.selectbox("Company", ["MC", "ACME", "Globex"])
year = st.sidebar.selectbox("Year", ["All Years", "2023", "2024"])

# ---- Mock Data ----
data = {
    "Quarter": ["2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2", "2024 Q3", "2024 Q4"],
    "Sales": [900, 1800, 1600, 2100, 2000, 2200, 2400, 2600],
    "Profit": [50, 75, 150, 180, 200, 220, 230, 250],
}

df = pd.DataFrame(data)

# ---- KPI Cards ----
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
profit_margin = (total_profit / total_sales) * 100
growth_rate = ((df["Sales"].iloc[-1] - df["Sales"].iloc[0]) / df["Sales"].iloc[0]) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales Volume", f"{total_sales:,}")
col2.metric("Total Profit", f"${total_profit:,}")
col3.metric("Average Profit Margin", f"{profit_margin:.2f}%", delta="Below Target")
col4.metric("Growth Rate", f"{growth_rate:.1f}%", delta="Growing")

st.markdown("---")

# ---- Charts ----
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Sales Volume Trends")
    fig_sales = px.bar(df, x="Quarter", y="Sales", text="Sales", title="Quarterly Sales Volume")
    st.plotly_chart(fig_sales, use_container_width=True)

with right_col:
    st.subheader("💰 Profit Analysis")
    fig_profit = px.scatter(df, x="Quarter", y="Profit", size="Profit", text="Profit",
                            title="Quarterly Profit Trends")
    st.plotly_chart(fig_profit, use_container_width=True)
