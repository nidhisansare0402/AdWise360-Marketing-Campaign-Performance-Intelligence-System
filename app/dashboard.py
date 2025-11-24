import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime, timedelta, timezone

from app.etl import get_cached_data, refresh_data
from app.data_loader import create_campaign_features, extract_platforms

st.set_page_config(page_title='AdWise360 Dashboard', layout='wide')
st.title('AdWise360 – Marketing Campaign Insights')

# load cached data
df = get_cached_data()

# platform mapping
platforms_df = extract_platforms()
if 'platform_name' in platforms_df.columns:
    name_col = 'platform_name'
else:
    name_col = platforms_df.columns[1] if len(platforms_df.columns)>1 else None
platform_map = dict(zip(platforms_df['platform_id'], platforms_df[name_col])) if name_col else {1:'Google Ads',2:'YouTube',3:'Facebook Ads'}

# filter options
friendly_platforms = ['All'] + [platform_map[i] for i in sorted(platform_map.keys())]
friendly_regions = ['All'] + sorted(df['region'].dropna().unique().tolist()) if not df.empty else ['All']
friendly_objectives = ['All'] + sorted(df['objective'].dropna().unique().tolist()) if not df.empty else ['All']

st.sidebar.header('Filters')
selected_platform_name = st.sidebar.selectbox('Platform', friendly_platforms)
selected_region = st.sidebar.selectbox('Region', friendly_regions)
selected_objective = st.sidebar.selectbox('Objective', friendly_objectives)

if st.sidebar.button('Refresh Data'):
    try:
        refresh_data()
        st.sidebar.success('Refreshed cache.')
    except Exception as e:
        st.sidebar.error('Refresh failed: ' + str(e))

# last refresh
IST = timezone(timedelta(hours=5, minutes=30))
last_refresh_iso = st.session_state.get('last_refresh', None)
if last_refresh_iso:
    try:
        last_dt = datetime.fromisoformat(last_refresh_iso).astimezone(IST)
        st.sidebar.write('Last refresh (IST): ' + last_dt.strftime('%Y-%m-%d %H:%M:%S'))
    except Exception:
        pass
else:
    st.sidebar.info('No refresh recorded for this session. Use Refresh to load fresh data.')

# export ML features
if st.sidebar.button('Export ML Features'):
    features = create_campaign_features(df)
    csv_bytes = features.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button('Download ML features', csv_bytes, file_name='ml_campaign_features.csv', mime='text/csv')

# apply filters
selected_platform_id = None
if selected_platform_name != 'All':
    selected_platform_id = next((k for k,v in platform_map.items() if v==selected_platform_name), None)

filtered = df.copy() if not df.empty else pd.DataFrame()
if selected_platform_id is not None and not filtered.empty:
    filtered = filtered[filtered['platform_id']==selected_platform_id]
if selected_region != 'All' and not filtered.empty:
    filtered = filtered[filtered['region']==selected_region]
if selected_objective != 'All' and not filtered.empty:
    filtered = filtered[filtered['objective']==selected_objective]

# KPI cards
st.subheader('Key Metrics')
if not filtered.empty:
    total_impressions = int(filtered['impressions'].sum())
    total_clicks = int(filtered['clicks'].sum())
    avg_ctr = round(filtered['CTR'].mean(),2)
    avg_cpc = round(filtered['CPC'].mean(),2)
    avg_roi = round(filtered['ROI'].mean(),2)
else:
    total_impressions = total_clicks = avg_ctr = avg_cpc = avg_roi = 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric('Total Impressions', f"{total_impressions:,}")
c2.metric('Total Clicks', f"{total_clicks:,}")
c3.metric('Avg CTR (%)', avg_ctr)
c4.metric('Avg CPC (₹)', avg_cpc)
c5.metric('Avg ROI (%)', avg_roi)

# tabs
tab1,tab2,tab3,tab4 = st.tabs(['Overview','Charts','Raw Data','Predictions'])

with tab1:
    st.write('### ROI Trend Over Time')
    if not filtered.empty:
        roi_trend = filtered.groupby('date')['ROI'].mean().sort_index()
        st.line_chart(roi_trend)
    else:
        st.info('No data for current filters.')

with tab2:
    st.write('### Impressions vs Clicks')
    if not filtered.empty:
        imp_clicks = filtered.groupby('date')[['impressions','clicks']].sum().sort_index()
        st.area_chart(imp_clicks)
    else:
        st.info('No data for current filters.')
    st.write('### CTR vs ROI Scatter')
    if not filtered.empty:
        scatter = alt.Chart(filtered).mark_circle(size=60).encode(x='CTR', y='ROI', tooltip=['campaign_name','CTR','ROI'])
        st.altair_chart(scatter, use_container_width=True)

with tab3:
    st.write('### Dataset (sample)')
    if not filtered.empty:
        display = filtered.copy()
        display['platform_name'] = display['platform_id'].map(platform_map)
        st.dataframe(display)
    else:
        st.info('No data to show.')

with tab4:
    st.write('### Predicted Campaign ROI')
    try:
        preds = pd.read_csv(PROJECT_ROOT / 'database' / 'predictions_output.csv')
        st.dataframe(preds)
        st.download_button('Download Predicted ROI (CSV)', preds.to_csv(index=False).encode('utf-8'), file_name='predicted_roi.csv')
    except Exception:
        st.info('No predictions available yet. Run ml/train_model.py and ml/generate_predictions.py to create predictions.')

# download filtered data
st.download_button('Download filtered data (CSV)', filtered.to_csv(index=False).encode('utf-8'), 'adwise_filtered.csv', 'text/csv')