import streamlit as st
from data_loader import load_to_df

@st.cache_data(ttl=300)  # cache for 5 minutes
def get_cached_data():
    return load_to_df()

def refresh_data():
    # clear cache and reload
    get_cached_data.clear()
    return get_cached_data()
