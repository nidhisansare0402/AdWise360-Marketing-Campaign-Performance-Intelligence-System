import pandas as pd
from sqlalchemy import create_engine, text
import os
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def get_db_engine_from_env():
    try:
        db_url = None
        if "DATABASE_URL" in st.secrets:
            db_url = st.secrets["DATABASE_URL"]
        elif "mysql" in st.secrets:
            # example structure in secrets.toml:
            # [mysql]
            # host = "..."
            # user = "..."
            # password = "..."
            # db = "..."
            mysql = st.secrets["mysql"]
            db_url = f"mysql+pymysql://{mysql['user']}:{mysql['password']}@{mysql['host']}:{mysql.get('port',3306)}/{mysql['db']}"
        if db_url:
            return create_engine(db_url)
    except Exception:
        pass

    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        return create_engine(db_url)

    local = os.environ.get("LOCAL_DB_URL")
    if local:
        return create_engine(local)

    raise RuntimeError("No DB connection configured (set Streamlit secrets or DATABASE_URL)")

@st.cache_data(ttl=600)
def get_cached_data():
    """
    Try DB first; if it fails, fallback to CSV files from repository.
    Returns joined DataFrame like earlier code expected.
    """
    # Attempt DB read
    try:
        engine = get_db_engine_from_env()
        query = """
        SELECT m.*, c.campaign_name, c.platform_id, c.objective, c.region, c.start_date, c.end_date, c.budget
        FROM metrics m
        JOIN campaigns c ON m.campaign_id = c.campaign_id;
        """
        df = pd.read_sql(text(query), engine)
        # compute CTR, CPC, ROI etc if needed — same logic you used previously
        df['CTR'] = (df['clicks'] / df['impressions']).fillna(0) * 100
        df['CPC'] = (df['spend'] / df['clicks']).replace([pd.NA, float('inf')], 0).fillna(0)
        df['ROI'] = (df['revenue'] / df['spend']).replace([pd.NA, float('inf')], 0).fillna(0)
        return df
    except Exception as e:
        # LOG and fallback
        st.warning(f"DB connection failed: {e} — falling back to CSV files from repo.")
        try:
            root = PROJECT_ROOT
            metrics_csv = root / "database" / "metrics.csv"
            campaigns_csv = root / "database" / "campaigns.csv"
            if metrics_csv.exists() and campaigns_csv.exists():
                metrics_df = pd.read_csv(metrics_csv)
                campaigns_df = pd.read_csv(campaigns_csv)
                df = metrics_df.merge(campaigns_df, on="campaign_id", how="left")
                # compute CTR/CPC/ROI same as above
                df['CTR'] = (df['clicks'] / df['impressions']).fillna(0) * 100
                df['CPC'] = (df['spend'] / df['clicks']).replace([pd.NA, float('inf')], 0).fillna(0)
                df['ROI'] = (df['revenue'] / df['spend']).replace([pd.NA, float('inf')], 0).fillna(0)
                return df
            else:
                # if CSVs not present, return empty DataFrame
                st.error("CSV fallback files not found in /database. Please commit metrics.csv and campaigns.csv to the repo.")
                return pd.DataFrame()
        except Exception as e2:
            st.error(f"CSV fallback failed: {e2}")
            return pd.DataFrame()
