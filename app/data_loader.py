import pandas as pd
from sqlalchemy import text
from app.db_connection import get_db_connection
import numpy as np

def extract_campaigns():
    engine = get_db_connection()
    q = "SELECT * FROM campaigns;"
    return pd.read_sql(text(q), engine)

def extract_metrics():
    engine = get_db_connection()
    q = "SELECT * FROM metrics;"
    return pd.read_sql(text(q), engine)

def extract_platforms():
    engine = get_db_connection()
    q = "SELECT platform_id, name FROM platforms;"
    return pd.read_sql(text(q), engine)

def transform_joined(campaigns_df, metrics_df):
    # join metrics with campaigns (left join ensures metrics keep their rows)
    df = metrics_df.merge(campaigns_df, on="campaign_id", how="left")

    # safe computations: if missing value fill with zero
    df['impressions'] = df['impressions'].fillna(0)
    df['clicks'] = df['clicks'].fillna(0)
    df['conversions'] = df['conversions'].fillna(0)
    df['spend'] = df['spend'].fillna(0)
    df['revenue'] = df['revenue'].fillna(0)

    # compute KPIs 
    df['CTR'] = (df['clicks'] / df['impressions']).fillna(0) * 100
    df['CPC'] = (df['spend'] / df['clicks']).replace([float('inf'), -float('inf')], 0).fillna(0)  # replace handles infinity and negative infinity 
    df['CPA'] = (df['spend'] / df['conversions']).replace([float('inf'), -float('inf')], 0).fillna(0)
    df['ROI'] = ((df['revenue'] - df['spend']) / df['spend']).replace([float('inf'), -float('inf')], 0).fillna(0) * 100

    # ensure date is a datetime for plotting
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_to_df():
    # Orchestration: extract -> transform -> return final DataFrame
    campaigns = extract_campaigns()
    metrics = extract_metrics()
    df = transform_joined(campaigns, metrics)
    return df  # this df is ready to use dataframe for dashboards, charts

# Small helper to aggregate campaign-level features for ML # it becomes input for ML models
def create_campaign_features(df):

    if 'campaign_id' not in df.columns:
        raise ValueError("create_campaign_features expects 'campaign_id' column. Found: " + ", ".join(df.columns))

    # 1. Aggregate campaign-level metrics
    agg = df.groupby(['campaign_id', 'campaign_name', 'platform_id', 'objective', 'region']).agg(
        total_impressions=('impressions', 'sum'),
        total_clicks=('clicks', 'sum'),
        total_conversions=('conversions', 'sum'),
        total_spend=('spend', 'sum'),
        total_revenue=('revenue', 'sum'),
        avg_ctr=('CTR', 'mean'),
        avg_roi=('ROI', 'mean'),
        days_active=('date', 'count'),
        budget=('budget', 'mean')  # ensure budget included
    ).reset_index()

    features_df = agg.copy()

    # 2. Add engineered features  

    # SAFE columns (avoid divide-by-zero)
    features_df['total_spend_safe'] = features_df['total_spend'].replace(0, 1)
    features_df['total_clicks_safe'] = features_df['total_clicks'].replace(0, 1)
    features_df['budget_safe'] = features_df['budget'].replace(0, 1)

    # Engagement efficiency
    features_df['clicks_per_rupee'] = features_df['total_clicks'] / features_df['total_spend_safe']
    features_df['revenue_per_click'] = features_df['total_revenue'] / features_df['total_clicks_safe']
    features_df['conversions_per_click'] = features_df['total_conversions'] / features_df['total_clicks_safe']

    # Budget ratio
    features_df['budget_utilization'] = features_df['total_spend'] / features_df['budget_safe']

    # Profit + log transforms
    features_df['profit'] = features_df['total_revenue'] - features_df['total_spend']
    features_df['log_revenue'] = np.log1p(features_df['total_revenue'].clip(lower=0))
    features_df['log_spend'] = np.log1p(features_df['total_spend'].clip(lower=0))
    features_df['log_profit'] = np.log1p(features_df['profit'].clip(lower=0))

    # One-hot encoding for platform and objective
    platform_dummies = pd.get_dummies(features_df['platform_id'], prefix='platform', drop_first=True)
    obj_dummies = pd.get_dummies(features_df['objective'], prefix='obj', drop_first=True)

    features_df = pd.concat([features_df, platform_dummies, obj_dummies], axis=1)

    # Cleanup
    features_df.drop(columns=['total_spend_safe', 'total_clicks_safe', 'budget_safe'], inplace=True, errors='ignore')
    features_df = features_df.replace([np.inf, -np.inf], np.nan).fillna(0)

    return features_df

def extract_predictions():
    # If you create a predictions table later, this reads it
    engine = get_db_connection()
    q = "SELECT * FROM predictions;"
    return pd.read_sql(text(q), engine)
