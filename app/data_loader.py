import pandas as pd
from db_connection import get_db_connection

def load_campaign_data():
    engine = get_db_connection()
    query = "SELECT * FROM campaigns;"
    df = pd.read_sql(query, engine)
    return df

def load_metrics_data():
    engine = get_db_connection()
    query = "SELECT * FROM metrics;"
    df = pd.read_sql(query, engine)
    return df

def load_joined_data():
    engine = get_db_connection()

    query = """
    SELECT 
        c.campaign_id,
        c.campaign_name,
        c.platform_id,
        c.region,
        c.objective,
        m.date,
        m.impressions,
        m.clicks,
        m.conversions,
        m.spend,
        m.revenue
    FROM campaigns c
    JOIN metrics m ON c.campaign_id = m.campaign_id;
    """

    df = pd.read_sql(query, engine)

    # Compute KPIs
    df['CTR'] = round(df['clicks'] / df['impressions'] * 100, 2)
    df['CPC'] = round(df['spend'] / df['clicks'], 2)
    df['CPA'] = round(df['spend'] / df['conversions'], 2)
    df['ROI'] = round((df['revenue'] - df['spend']) / df['spend'] * 100, 2)

    return df
