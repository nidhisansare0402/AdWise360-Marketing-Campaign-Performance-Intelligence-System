import streamlit as st
from data_loader import load_joined_data

st.set_page_config(
    page_title="AdWise360 Dashboard", 
    layout="wide"
)

# Load data
df = load_joined_data()

st.title("AdWise360 – Marketing Campaign Performance Dashboard")

st.sidebar.header("Filters")

platforms = df['platform_id'].unique()
regions = df['region'].unique()
objectives = df['objective'].unique()

selected_platform = st.sidebar.selectbox("Select Platform", platforms)
selected_region = st.sidebar.selectbox("Select Region", regions)
selected_objective = st.sidebar.selectbox("Select Objective", objectives)

# Filter data
filtered_df = df[
    (df['platform_id'] == selected_platform) &
    (df['region'] == selected_region) &
    (df['objective'] == selected_objective)
]

st.write("### Filtered Campaign Data")
st.dataframe(filtered_df)
