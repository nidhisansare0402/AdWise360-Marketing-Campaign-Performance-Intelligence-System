import pandas as pd
import numpy as np

# Minimal helper functions: create_campaign_features and extract_platforms

def create_campaign_features(df):
    """Aggregate row-level metrics into campaign-level features CSV for ML."""
    if df.empty:
        return pd.DataFrame()

    # ensure numeric
    df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce').fillna(0)
    df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce').fillna(0)
    df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce').fillna(0)
    df['spend'] = pd.to_numeric(df['spend'], errors='coerce').fillna(0)
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)

    agg = df.groupby(['campaign_id','campaign_name','platform_id','objective','region']).agg(
        total_impressions=('impressions','sum'),
        total_clicks=('clicks','sum'),
        total_conversions=('conversions','sum'),
        total_spend=('spend','sum'),
        total_revenue=('revenue','sum'),
        start_date=('start_date','first'),
        end_date=('end_date','first'),
        budget=('budget','first')
    ).reset_index()

    agg['days_active'] = (pd.to_datetime(agg['end_date']) - pd.to_datetime(agg['start_date'])).dt.days.fillna(0).astype(int)
    agg['avg_ctr'] = (agg['total_clicks'] / agg['total_impressions']).replace([np.inf, np.nan], 0) * 100
    agg['conv_rate'] = (agg['total_conversions'] / agg['total_clicks']).replace([np.inf, np.nan], 0)
    agg['avg_cpc'] = (agg['total_spend'] / agg['total_clicks']).replace([np.inf, np.nan], 0)
    agg['avg_roi'] = (agg['total_revenue'] / agg['total_spend']).replace([np.inf, np.nan], 0)
    agg['profit'] = agg['total_revenue'] - agg['total_spend']

    # engineered features
    agg['clicks_per_rupee'] = agg['total_clicks'] / agg['total_spend'].replace({0:1})
    agg['revenue_per_click'] = agg['total_revenue'] / agg['total_clicks'].replace({0:1})
    agg['conversions_per_click'] = agg['total_conversions'] / agg['total_clicks'].replace({0:1})
    agg['budget_utilization'] = agg['total_spend'] / agg['budget'].replace({0:1})

    # one-hot platform/objective
    platform_dummies = pd.get_dummies(agg['platform_id'], prefix='platform', drop_first=True)
    obj_dummies = pd.get_dummies(agg['objective'], prefix='obj', drop_first=True)
    features = pd.concat([agg, platform_dummies, obj_dummies], axis=1)

    # ensure no infs
    features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
    return features


def extract_platforms():
    """Return small DataFrame mapping platform_id -> platform_name. Uses static mapping if not present."""
    # If you have a platforms table or file, read it; otherwise return default map
    try:
        # attempt to read platforms.csv if present
        p = Path(__file__).resolve().parents[1] / 'database' / 'platforms.csv'
        if p.exists():
            return pd.read_csv(p)
    except Exception:
        pass

    return pd.DataFrame({'platform_id':[1,2,3], 'platform_name':['Google Ads','YouTube','Facebook Ads']})