from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_DIR = PROJECT_ROOT / "database"

METRICS_CSV = DATABASE_DIR / "metrics.csv"
CAMPAIGNS_CSV = DATABASE_DIR / "campaigns.csv"

@st.cache_data(ttl=600)
def get_cached_data():
    """
    Read CSVs, join metrics + campaigns, compute KPIs and return DataFrame.
    Cached for 10 minutes by default.
    """
    # Check files
    if not METRICS_CSV.exists() or not CAMPAIGNS_CSV.exists():
        st.error(f"CSV fallback missing. Ensure {METRICS_CSV} and {CAMPAIGNS_CSV} exist in repository.")
        return pd.DataFrame()

    # Read CSVs
    try:
        metrics = pd.read_csv(METRICS_CSV)
    except Exception as e:
        st.error(f"Failed to read metrics CSV: {e}")
        return pd.DataFrame()

    try:
        campaigns = pd.read_csv(CAMPAIGNS_CSV)
    except Exception as e:
        st.error(f"Failed to read campaigns CSV: {e}")
        return pd.DataFrame()

    # Join
    try:
        df = metrics.merge(campaigns, on="campaign_id", how="left", validate="m:1")
    except Exception:
        # fallback: conservative merge
        df = pd.merge(metrics, campaigns, on="campaign_id", how="left")

    # Normalize numeric columns (safe conversion)
    for col in ["impressions", "clicks", "conversions", "spend", "revenue", "budget"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    # Dates
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        except Exception:
            pass

    # KPIs (safe math; avoid divide-by-zero)
    df["CTR"] = (df["clicks"] / df["impressions"]).replace([np.inf, -np.inf], 0).fillna(0) * 100
    df["CPC"] = (df["spend"] / df["clicks"]).replace([np.inf, -np.inf], 0).fillna(0)
    df["ROI"] = (df["revenue"] / df["spend"]).replace([np.inf, -np.inf], 0).fillna(0)

    # Keep consistent column types / names expected by the rest of pipeline
    # e.g., campaign_id, campaign_name, platform_id, objective, region, start_date, end_date, budget
    expected_cols = ["campaign_id","campaign_name","platform_id","objective","region","start_date","end_date","budget"]
    for c in expected_cols:
        if c not in df.columns:
            df[c] = np.nan

    return df

def refresh_data():
    """
    Clear the cached get_cached_data() and write a last_refresh timestamp into st.session_state.
    Call this from a Streamlit button (on_click) or in UI code when needed.
    """
    # Clear cache for get_cached_data (works when it's decorated with @st.cache_data)
    try:
        get_cached_data.clear()
    except Exception:
        try:
            st.cache_data.clear()
        except Exception:
            pass

    # Set last refresh timestamp (UTC ISO format)
    try:
        st.session_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
    except Exception:
        # session_state might not exist in certain contexts, ignore silently
        pass

    return True
