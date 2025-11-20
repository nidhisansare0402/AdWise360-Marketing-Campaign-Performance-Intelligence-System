import pandas as pd
from sqlalchemy import text
from db_connection import get_db_connection

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
    # Group by campaign and produce aggregated features for modeling
    agg = df.groupby(['campaign_id','campaign_name','platform_id','objective','region']).agg(
        total_impressions=('impressions','sum'),
        total_clicks=('clicks','sum'),
        total_conversions=('conversions','sum'),
        total_spend=('spend','sum'),
        total_revenue=('revenue','sum'),
        avg_ctr=('CTR','mean'),
        avg_roi=('ROI','mean'),
        days_active=('date','nunique')
    ).reset_index()

    # derived features
    agg['conv_rate'] = agg['total_conversions'] / agg['total_clicks'].replace(0,1)
    agg['profit'] = agg['total_revenue'] - agg['total_spend']
    return agg

def extract_predictions():
    # If you create a predictions table later, this reads it
    engine = get_db_connection()
    q = "SELECT * FROM predictions;"
    return pd.read_sql(text(q), engine)
