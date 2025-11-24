# app/app.py
# AdWise360 Streamlit dashboard - cleaned, defensive, and easy to explain.

# ---------- DEV: ensure project root is on sys.path (helps Streamlit find 'app' package) ----------
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]  # project root is two levels up from this file
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ---------- Standard imports ----------
import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime, timezone, timedelta

# ---------- App imports (package-style) ----------
from app.etl import get_cached_data, refresh_data
from app.data_loader import create_campaign_features, extract_platforms, extract_predictions

# ---------- Page config ----------
st.set_page_config(page_title="AdWise360 Dashboard", layout="wide")
st.title("AdWise360 – Marketing Campaign Insights")

# ---------- Load data (cached) ----------
# get_cached_data uses @st.cache_data to keep UI snappy
try:
    df = get_cached_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = pd.DataFrame()  # safe fallback

# ---------- Platform name mapping (defensive) ----------
platform_map = {}
try:
    platforms_df = extract_platforms()
    # detect correct platform name column (flexible)
    if 'platform_name' in platforms_df.columns:
        name_col = 'platform_name'
    elif 'name' in platforms_df.columns:
        name_col = 'name'
    else:
        # if the table exists but has different column names, try to use second column
        cols = list(platforms_df.columns)
        name_col = cols[1] if len(cols) > 1 else None

    if name_col:
        platform_map = dict(zip(platforms_df['platform_id'], platforms_df[name_col]))
    else:
        # fallback: simple numeric names
        platform_map = {int(r): f"Platform_{int(r)}" for r in platforms_df['platform_id'].tolist()}
except Exception:
    # If platforms table not available, use a safe default mapping
    platform_map = {1: "Google Ads", 2: "YouTube", 3: "Facebook Ads"}

# build friendly lists for filters
friendly_platforms = ["All"] + [platform_map[i] for i in sorted(platform_map.keys())]
friendly_regions = ["All"]
friendly_objectives = ["All"]

if not df.empty:
    friendly_regions = ["All"] + sorted(df['region'].dropna().unique().tolist())
    friendly_objectives = ["All"] + sorted(df['objective'].dropna().unique().tolist())

# ---------- Sidebar: filters and actions ----------
st.sidebar.header("Filters")
selected_platform_name = st.sidebar.selectbox("Platform", friendly_platforms)
selected_region = st.sidebar.selectbox("Region", friendly_regions)
selected_objective = st.sidebar.selectbox("Objective", friendly_objectives)

# Refresh button
if st.sidebar.button("Refresh Data"):
    try:
        refresh_data()
        st.sidebar.success("Refreshed cache.")
    except Exception as e:
        st.sidebar.error("Refresh failed: " + str(e))

# Last refresh indicator (IST shown)
IST = timezone(timedelta(hours=5, minutes=30))
last_refresh_iso = st.session_state.get('last_refresh', None)
if last_refresh_iso:
    try:
        last_dt = datetime.fromisoformat(last_refresh_iso)
    except Exception:
        last_dt = datetime.now(timezone.utc)
    # display in IST
    last_dt_ist = last_dt.astimezone(IST)
    age = datetime.now(IST) - last_dt_ist
    st.sidebar.write(f"Last refresh (IST): {last_dt_ist.strftime('%Y-%m-%d %H:%M:%S')}")
    if age > timedelta(minutes=10):
        st.sidebar.warning(f"Data may be stale ({int(age.total_seconds()/60)} min ago). Use Refresh.")
else:
    st.sidebar.info("No refresh recorded for this session. Use Refresh to load fresh data.")

# Export ML features (download directly in the sidebar)
if st.sidebar.button("Export ML Features"):
    try:
        if df.empty:
            st.sidebar.error("No data to export. Ensure DB or CSV is available.")
        else:
            features = create_campaign_features(df)
            csv_bytes = features.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button("Download ML features", csv_bytes, file_name="ml_campaign_features.csv", mime="text/csv")
            st.sidebar.success("ML features prepared for download.")
    except Exception as e:
        st.sidebar.error("Export failed: " + str(e))

# ---------- Apply filters ----------
# convert platform selection back to id
selected_platform_id = None
if selected_platform_name != "All":
    # reverse lookup
    try:
        selected_platform_id = next(k for k, v in platform_map.items() if v == selected_platform_name)
    except StopIteration:
        selected_platform_id = None

filtered = df.copy() if not df.empty else pd.DataFrame()
if selected_platform_id is not None and not filtered.empty:
    filtered = filtered[filtered['platform_id'] == selected_platform_id]
if selected_region != "All" and not filtered.empty:
    filtered = filtered[filtered['region'] == selected_region]
if selected_objective != "All" and not filtered.empty:
    filtered = filtered[filtered['objective'] == selected_objective]

# ---------- KPI cards ----------
st.subheader("Key Metrics")
if not filtered.empty:
    total_impressions = int(filtered['impressions'].sum())
    total_clicks = int(filtered['clicks'].sum())
    avg_ctr = round(filtered['CTR'].mean(), 2)
    avg_cpc = round(filtered['CPC'].mean(), 2)
    avg_roi = round(filtered['ROI'].mean(), 2)
else:
    total_impressions = total_clicks = avg_ctr = avg_cpc = avg_roi = 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Impressions", f"{total_impressions:,}")
c2.metric("Total Clicks", f"{total_clicks:,}")
c3.metric("Avg CTR (%)", avg_ctr)
c4.metric("Avg CPC (₹)", avg_cpc)
c5.metric("Avg ROI (%)", avg_roi)

# ---------- Tabs ----------
tab_overview, tab_charts, tab_raw, tab_preds = st.tabs(["Overview", "Charts", "Raw Data", "Predictions"])

with tab_overview:
    st.write("### ROI Trend Over Time")
    if not filtered.empty:
        roi_trend = filtered.groupby("date")["ROI"].mean().sort_index()
        st.line_chart(roi_trend)
    else:
        st.info("No data for current filters.")

with tab_charts:
    st.write("### Impressions vs Clicks")
    if not filtered.empty:
        imp_clicks = filtered.groupby("date")[["impressions", "clicks"]].sum().sort_index()
        st.area_chart(imp_clicks)
    else:
        st.info("No data for current filters.")

    st.write("### CTR vs ROI Scatter")
    if not filtered.empty:
        scatter = alt.Chart(filtered).mark_circle(size=60).encode(
            x='CTR',
            y='ROI',
            tooltip=['campaign_name', 'CTR', 'ROI']
        )
        st.altair_chart(scatter, use_container_width=True)
    else:
        st.info("No data for current filters.")

with tab_raw:
    st.write("### Dataset (sample)")
    if not filtered.empty:
        display = filtered.copy()
        display['platform_name'] = display['platform_id'].map(platform_map)
        st.dataframe(display)
    else:
        st.info("No data to show.")

with tab_preds:
    st.write("### Predicted Campaign ROI")
    # show model info
    model_info = "rf_tuned.pkl"
    try:
        import joblib, os
        model_path = os.path.join("ml_models", model_info)
        if os.path.exists(model_path):
            st.sidebar.success(f"Using model: {model_info}")
        else:
            st.sidebar.info("No trained model found; run ml/train_model.py")
    except Exception:
        pass

    try:
        preds = pd.read_csv("database/predictions_output.csv")
        # optionally show only relevant columns
        cols_to_show = ['campaign_id','campaign_name','platform_id','objective','region',
                        'total_impressions','total_clicks','total_conversions',
                        'total_spend','total_revenue','avg_roi','predicted_roi']
        display = preds[cols_to_show] if set(cols_to_show).issubset(preds.columns) else preds
        st.dataframe(display)
        st.download_button(
            label="Download Predicted ROI (CSV)",
            data=preds.to_csv(index=False).encode('utf-8'),
            file_name="predicted_roi.csv",
            mime="text/csv"
        )
    except FileNotFoundError:
        st.info("No predictions available yet. Run your ML script to generate predictions.")

# ---------- Download filtered data ----------
st.write("")  # spacing
st.download_button("Download filtered data (CSV)", filtered.to_csv(index=False).encode('utf-8'), "adwise_filtered.csv", "text/csv")
