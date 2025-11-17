import streamlit as st
from etl import get_cached_data, refresh_data
from data_loader import create_campaign_features, save_ml_features_csv
import io

st.set_page_config(page_title="AdWise360 Dashboard", layout="wide")

st.title("AdWise360 – Marketing Campaign Insights")

df = get_cached_data()

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

st.subheader("Impressions vs Clicks")
imp_clicks = filtered.groupby("date")[["impressions", "clicks"]].sum()
st.area_chart(imp_clicks)

import altair as alt

st.subheader("CTR vs ROI Scatter Plot")
scatter = alt.Chart(filtered).mark_circle(size=60).encode(
    x='CTR',
    y='ROI',
    tooltip=['campaign_name', 'CTR', 'ROI']
)
st.altair_chart(scatter, use_container_width=True)

tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Raw Data"])

with tab1:
    st.write("### KPI Summary")
    

with tab2:
    st.write("### Visual Charts")
    

with tab3:
    st.write("### Dataset")
    st.dataframe(filtered)

st.sidebar.button("Refresh Data", on_click=refresh_data)

# ML export button
if st.sidebar.button("Export ML Features (CSV)"):
    features = create_campaign_features(df)
    save_ml_features_csv(features)
    st.success("Saved features to database/ml_campaign_features.csv")

# Download filtered CSV
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("Download filtered data (CSV)", data=csv, file_name="adwise_filtered.csv", mime="text/csv")