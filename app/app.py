import streamlit as st
from data_loader import load_joined_data

st.set_page_config(page_title="AdWise360 Dashboard", layout="wide")

st.title("AdWise360 – Marketing Campaign Insights")

df = load_joined_data()

# --- FILTERS ---
st.sidebar.header("Filters")
platform = st.sidebar.selectbox("Platform", df['platform_id'].unique())
region = st.sidebar.selectbox("Region", df['region'].unique())
objective = st.sidebar.selectbox("Objective", df['objective'].unique())

filtered = df[
    (df['platform_id'] == platform) &
    (df['region'] == region) &
    (df['objective'] == objective)
]

# --- KPIs ---
total_impressions = int(filtered['impressions'].sum())
total_clicks = int(filtered['clicks'].sum())
avg_ctr = round(filtered['CTR'].mean(), 2)
avg_cpc = round(filtered['CPC'].mean(), 2)
avg_roi = round(filtered['ROI'].mean(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Clicks", f"{total_clicks:,}")
col3.metric("Avg CTR (%)", avg_ctr)
col4.metric("Avg CPC (₹)", avg_cpc)
col5.metric("Avg ROI (%)", avg_roi)

st.subheader("ROI Trend Over Time")
roi_trend = filtered.groupby("date")["ROI"].mean()
st.line_chart(roi_trend)
