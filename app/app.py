import streamlit as st
import altair as alt
from etl import get_cached_data, refresh_data
from data_loader import (
    create_campaign_features,
    save_ml_features_csv,
    extract_platforms
)
import pandas as pd

st.set_page_config(page_title="AdWise360 Dashboard", layout="wide")
st.title("AdWise360 – Marketing Campaign Insights")

# Load data ONCE (cached)
df = get_cached_data()

# Load platform names (from DB) and build mapping
try:
    platforms_df = extract_platforms()  # expects columns: platform_id, platform_name
    platform_map = dict(zip(platforms_df['platform_id'], platforms_df['platform_name']))
except Exception:
    # fallback mapping if platforms table not available
    platform_map = {1: "Google Ads", 2: "YouTube", 3: "Facebook Ads"}

# Build friendly lists for sidebar (include "All")
friendly_platforms = ["All"] + [platform_map[i] for i in sorted(platform_map.keys())]
friendly_regions = ["All"] + sorted(df['region'].dropna().unique().tolist())
friendly_objectives = ["All"] + sorted(df['objective'].dropna().unique().tolist())

# --- SIDEBAR FILTERS (single controls)
st.sidebar.header("Filters")
selected_platform_name = st.sidebar.selectbox("Platform", friendly_platforms)
selected_region = st.sidebar.selectbox("Region", friendly_regions)
selected_objective = st.sidebar.selectbox("Objective", friendly_objectives)

# Convert friendly platform name back to id (None => All)
if selected_platform_name == "All":
    selected_platform_id = None
else:
    selected_platform_id = next(k for k,v in platform_map.items() if v == selected_platform_name)

# Apply filters to create filtered DataFrame
filtered = df.copy()
if selected_platform_id is not None:
    filtered = filtered[filtered['platform_id'] == selected_platform_id]
if selected_region != "All":
    filtered = filtered[filtered['region'] == selected_region]
if selected_objective != "All":
    filtered = filtered[filtered['objective'] == selected_objective]

# --- KPIs ---
total_impressions = int(filtered['impressions'].sum()) if not filtered.empty else 0
total_clicks = int(filtered['clicks'].sum()) if not filtered.empty else 0
avg_ctr = round(filtered['CTR'].mean(), 2) if not filtered.empty else 0
avg_cpc = round(filtered['CPC'].mean(), 2) if not filtered.empty else 0
avg_roi = round(filtered['ROI'].mean(), 2) if not filtered.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Impressions", f"{total_impressions:,}")
col2.metric("Total Clicks", f"{total_clicks:,}")
col3.metric("Avg CTR (%)", avg_ctr)
col4.metric("Avg CPC (₹)", avg_cpc)
col5.metric("Avg ROI (%)", avg_roi)

# --- Tabs & Charts ---
tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Raw Data"])

with tab1:
    st.subheader("ROI Trend Over Time")
    if not filtered.empty:
        roi_trend = filtered.groupby("date")["ROI"].mean().sort_index()
        st.line_chart(roi_trend)
    else:
        st.info("No data for selected filters.")

with tab2:
    st.subheader("Impressions vs Clicks")
    if not filtered.empty:
        imp_clicks = filtered.groupby("date")[["impressions", "clicks"]].sum().sort_index()
        st.area_chart(imp_clicks)
    else:
        st.info("No data for selected filters.")

    st.subheader("CTR vs ROI Scatter Plot")
    if not filtered.empty:
        scatter = alt.Chart(filtered).mark_circle(size=60).encode(
            x='CTR',
            y='ROI',
            tooltip=['campaign_name', 'CTR', 'ROI']
        )
        st.altair_chart(scatter, use_container_width=True)
    else:
        st.info("No data for selected filters.")

with tab3:
    st.write("### Dataset")
    st.dataframe(filtered)

# --- Sidebar actions ---
if st.sidebar.button("Refresh Data"):
    try:
        refresh_data()
        st.sidebar.success("Data refreshed (cache invalidated). Reload the page if necessary.")
    except Exception as e:
        st.sidebar.error(f"Refresh failed: {e}")

if st.sidebar.button("Export ML Features (CSV)"):
    features = create_campaign_features(filtered)  # use filtered to respect selections
    # Save to disk (optional)
    save_ml_features_csv(features)
    # Provide browser download
    csv_bytes = features.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "Download ML features (CSV)",
        data=csv_bytes,
        file_name="ml_campaign_features.csv",
        mime="text/csv"
    )
    st.sidebar.success("Saved features and prepared download.")

# Download filtered CSV (main area)
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("Download filtered data (CSV)", data=csv, file_name="adwise_filtered.csv", mime="text/csv")
