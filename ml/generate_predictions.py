import joblib
import os
import pandas as pd
from app.data_loader import create_campaign_features

# 1. load raw transformed df from database/csv fallback
# we rely on app/etl.get_cached_data for the UI; here read CSV fallback
raw = pd.read_csv('database/metrics.csv')
campaigns = pd.read_csv('database/campaigns.csv')
df = raw.merge(campaigns, on='campaign_id', how='left')

# 2. build features
features = create_campaign_features(df)

# 3. load model
model_path = 'ml_models/rf_tuned.pkl'
if not os.path.exists(model_path):
    raise FileNotFoundError('Model not found. Run ml/train_model.py first.')
model = joblib.load(model_path)

# 4. prepare model input
cols = [c for c in [
    'total_impressions','total_clicks','total_conversions','total_spend','total_revenue',
    'avg_ctr','days_active','conv_rate','profit','clicks_per_rupee','revenue_per_click',
    'conversions_per_click','budget_utilization','log_revenue','log_spend','log_profit'
] if c in features.columns]
X = features[cols]

features['predicted_roi'] = model.predict(X)

os.makedirs('database', exist_ok=True)
features.to_csv('database/predictions_output.csv', index=False)
print('Saved predictions to database/predictions_output.csv')