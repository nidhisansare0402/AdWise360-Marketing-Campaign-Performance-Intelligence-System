# app/data_loader.py
import pandas as pd
from sqlalchemy import text
from db_connection import get_db_connection

def extract_campaigns():
    engine = get_db_connection()
    q = "SELECT * FROM campaigns;"
    return pd.read_sql(q, engine)

def extract_metrics():
    engine = get_db_connection()
    q = "SELECT * FROM metrics;"
    return pd.read_sql(q, engine)

def transform_joined(campaigns_df, metrics_df):
    # join
    df = metrics_df.merge(campaigns_df, on="campaign_id", how="left")
    # safe calculations
    df['CTR'] = (df['clicks'] / df['impressions']).fillna(0) * 100
    df['CPC'] = (df['spend'] / df['clicks']).replace([float('inf'), -float('inf')], 0).fillna(0)
    df['CPA'] = (df['spend'] / df['conversions']).replace([float('inf'), -float('inf')], 0).fillna(0)
    df['ROI'] = ((df['revenue'] - df['spend']) / df['spend']).replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    # parse date
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_to_df():
    campaigns = extract_campaigns()
    metrics = extract_metrics()
    return transform_joined(campaigns, metrics)

def create_campaign_features(df):
    # group by campaign
    agg = df.groupby(['campaign_id','campaign_name','platform_id','objective','region']).agg(
        total_impressions=('impressions','sum'),
        total_clicks=('clicks','sum'),
        total_conversions=('conversions','sum'),
        total_spend=('spend','sum'),
        total_revenue=('revenue','sum'),
        avg_ctr=('CTR','mean'),
        avg_cpc=('CPC','mean'),
        avg_roi=('ROI','mean'),
        days_active=('date','nunique')
    ).reset_index()

    # Derived features
    agg['conv_rate'] = agg['total_conversions'] / agg['total_clicks'].replace(0,1)
    agg['profit'] = agg['total_revenue'] - agg['total_spend']
    # Fill & types
    agg = agg.fillna(0)
    return agg

def save_ml_features_csv(agg_df, path='database/ml_campaign_features.csv'):
    agg_df.to_csv(path, index=False)

#Fetch platforms table
def extract_platforms():
    engine = get_db_connection()
    q = "SELECT platform_id, name FROM platforms;"
    return pd.read_sql(q, engine)