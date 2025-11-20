import streamlit as st
from data_loader import load_to_df
from datetime import datetime, timezone, timedelta

"""If you call this function again within 5 minutes (300 seconds) 
it will NOT call the database again.
Instead, it returns cached data == super fast."""
@st.cache_data(ttl=300) 
# catching function that loads DB

def get_cached_data():
    # This loads data from DB via data_loader.load_to_df()
    return load_to_df()

def refresh_data():
    """
    Clears the cached data and records a last_refresh timestamp in session_state.
    The function returns the fresh data (so UI can read it again).
    """
    #This line deletes the stored cached data so the next call will fetch new data.
    get_cached_data.clear()

    # IST timezone
    IST = timezone(timedelta(hours=5, minutes=30))

    # record refresh time in IST
    st.session_state['last_refresh'] = datetime.now(IST).isoformat()

    # return fresh data (cached again on next call)
    return get_cached_data()
