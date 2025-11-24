import pandas as pd
import os
from pathlib import Path
import streamlit as st
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def _get_engine_from_secrets_or_env():
    # Prefer Streamlit secrets, then env var. If missing, raise.
    try:
        if hasattr(st, 'secrets') and st.secrets:
            # support both DATABASE_URL or mysql dict
            if 'DATABASE_URL' in st.secrets:
                return create_engine(st.secrets['DATABASE_URL'])
            if 'mysql' in st.secrets:
                m = st.secrets['mysql']
                url = f"mysql+pymysql://{m['user']}:{m['password']}@{m['host']}:{m.get('port',3306)}/{m['db']}"
                return create_engine(url)
    except Exception:
        pass

    db_url = os.environ.get('DATABASE_URL') or os.environ.get('LOCAL_DB_URL')
    if db_url:
        return create_engine(db_url)

    raise RuntimeError('No DB configured (use Streamlit secrets or DATABASE_URL)')

@st.cache_data(ttl=600)
def get_cached_data():
    """
    Try DB first; if it fails, fallback to local CSVs in /database.
    Returns DataFrame with computed CTR/CPC/ROI columns.
    """
    # try DB
    try:
        engine = _get_engine_from_secrets_or_env()
        query = text(
            """
            SELECT m.*, c.campaign_name, c.platform_id, c.objective, c.region, c.start_date, c.end_date, c.budget
            FROM metrics m
            JOIN campaigns c ON m.campaign_id = c.campaign_id;
            """
        )
        df = pd.read_sql(query, engine)
    except Exception as e:
        # fallback to CSV files in repo
        st.warning(f"DB connection failed: {e} — using CSV fallback from /database")
        metrics_csv = PROJECT_ROOT / 'database' / 'metrics.csv'
        campaigns_csv = PROJECT_ROOT / 'database' / 'campaigns.csv'
        if metrics_csv.exists() and campaigns_csv.exists():
            metrics_df = pd.read_csv(metrics_csv)
            campaigns_df = pd.read_csv(campaigns_csv)
            df = metrics_df.merge(campaigns_df, on='campaign_id', how='left')
        else:
            st.error('No DB and CSV fallback not found in /database. Add metrics.csv and campaigns.csv to repo.')
            return pd.DataFrame()

    # compute KPIs safely
    df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
    df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce').fillna(0)
    df['spend'] = pd.to_numeric(df['spend'], errors='coerce').fillna(0)
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)

    df['CTR'] = (df['clicks'] / df['impressions']).replace([float('inf'), pd.NA], 0).fillna(0) * 100
    df['CPC'] = (df['spend'] / df['clicks']).replace([float('inf'), pd.NA], 0).fillna(0)
    df['ROI'] = (df['revenue'] / df['spend']).replace([float('inf'), pd.NA], 0).fillna(0)

    # ensure date column is datetime if present
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'])
        except Exception:
            pass

    return df


def refresh_data():
    """
    Clear cached get_cached_data and set last_refresh in session_state.
    """
    try:
        if 'get_cached_data' in globals():
            try:
                get_cached_data.clear()
            except Exception:
                try:
                    st.cache_data.clear()
                except Exception:
                    pass
    except Exception:
        pass

    try:
        st.session_state['last_refresh'] = datetime.now(timezone.utc).isoformat()
    except Exception:
        pass

    return True

