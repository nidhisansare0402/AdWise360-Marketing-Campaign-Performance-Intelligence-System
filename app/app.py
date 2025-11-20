import streamlit as st
import altair as alt
from etl import get_cached_data, refresh_data
from data_loader import (
    create_campaign_features,
    extract_platforms,
    extract_predictions
)
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="AdWise360 Dashboard", layout="wide")
st.title("AdWise360 – Marketing Campaign Insights")

# 1. Load data ONCE (cached)
df = get_cached_data()

# 2. Platform names mapping 
platforms_df = extract_platforms()
platform_map = dict(zip(platforms_df['platform_id'], platforms_df['name']))

# select lists with "All"
friendly_platforms = ["All"] + [platform_map[i] for i in sorted(platform_map.keys())]
friendly_regions = ["All"] + sorted(df['region'].dropna().unique().tolist())
friendly_objectives = ["All"] + sorted(df['objective'].dropna().unique().tolist())

# 3. Sidebar
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

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

# Last refresh indicator
last_refresh_iso = st.session_state.get('last_refresh', None)

if last_refresh_iso:
    # Convert stored timestamp to IST-aware datetime
    last_dt = datetime.fromisoformat(last_refresh_iso)

    # Current IST time
    now_ist = datetime.now(IST)

    # Time passed since last refresh
    age = now_ist - last_dt

    # Show formatted IST time
    st.sidebar.write(f"Last refresh: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    # If older than 10 minutes → show warning
    if age > timedelta(minutes=10):
        st.sidebar.warning(
            f"Data may be stale ({int(age.total_seconds()/60)} min ago). Use Refresh."
        )
else:
    st.sidebar.info("No refresh recorded for this session. Use Refresh to load fresh data.")

# Export ML features
if st.sidebar.button("Export ML Features"):
    try:
        features = create_campaign_features(df)  # you can use filtered below instead
        # Prepare for browser download
        csv_bytes = features.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Download ML features", csv_bytes, file_name="ml_campaign_features.csv", mime="text/csv")
        st.sidebar.success("ML features prepared for download.")
    except Exception as e:
        st.sidebar.error("Export failed: " + str(e))

# 4. Apply filters to build filtered DataFrame
# Convert platform name back to id
if selected_platform_name == "All":
    selected_platform_id = None
else:
    # reverse lookup
    selected_platform_id = next(k for k,v in platform_map.items() if v == selected_platform_name)

# Start from full df and filter step-by-step
filtered = df.copy()
if selected_platform_id is not None:
    filtered = filtered[filtered['platform_id'] == selected_platform_id]
if selected_region != "All":
    filtered = filtered[filtered['region'] == selected_region]
if selected_objective != "All":
    filtered = filtered[filtered['objective'] == selected_objective]

# 5. KPI cards
st.subheader("Key Metrics")
total_impressions = int(filtered['impressions'].sum()) if not filtered.empty else 0
total_clicks = int(filtered['clicks'].sum()) if not filtered.empty else 0
avg_ctr = round(filtered['CTR'].mean(), 2) if not filtered.empty else 0
avg_cpc = round(filtered['CPC'].mean(), 2) if not filtered.empty else 0
avg_roi = round(filtered['ROI'].mean(), 2) if not filtered.empty else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Impressions", f"{total_impressions:,}")
c2.metric("Total Clicks", f"{total_clicks:,}")
c3.metric("Avg CTR (%)", avg_ctr)
c4.metric("Avg CPC (₹)", avg_cpc)
c5.metric("Avg ROI (%)", avg_roi)

# 6. Tabs: Overview / Charts / Raw Data / Predictions
tab_overview, tab_charts, tab_raw, tab_preds = st.tabs(["Overview","Charts","Raw Data","Predictions"])

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
        imp_clicks = filtered.groupby("date")[["impressions","clicks"]].sum().sort_index()
        st.area_chart(imp_clicks)
    else:
        st.info("No data for current filters.")

    st.write("### CTR vs ROI Scatter")
    if not filtered.empty:
        scatter = alt.Chart(filtered).mark_circle(size=60).encode(
            x='CTR',
            y='ROI',
            tooltip=['campaign_name','CTR','ROI']
        )
        st.altair_chart(scatter, use_container_width=True)
    else:
        st.info("No data for current filters.")

with tab_raw:
    st.write("### Dataset (sample)")
    # show platform_name for readability
    display = filtered.copy()
    display['platform_name'] = display['platform_id'].map(platform_map)
    st.dataframe(display)

with tab_preds:
    st.write("### Predictions (if available)")
    try:
        preds = extract_predictions()
        if preds.empty:
            st.info("No predictions found. Export ML features and run training to populate predictions table.")
            # small example placeholder
            example = {
                "campaign_id":[101,102],
                "campaign_name":["Campaign_101","Campaign_102"],
                "predicted_roi":[120.5, 88.3],
                "ci_lower":[95.2,60.1],
                "ci_upper":[145.8,116.5]
            }
            st.dataframe(example)
        else:
            st.dataframe(preds)
            # allow download
            st.download_button("Download predictions CSV", preds.to_csv(index=False).encode('utf-8'), "predictions.csv", "text/csv")
    except Exception as e:
        st.info("Predictions unavailable: " + str(e))


# 7. Download the filtered data
st.write("")  # spacing
st.download_button("Download filtered data", filtered.to_csv(index=False).encode('utf-8'), "adwise_filtered.csv", "text/csv")
