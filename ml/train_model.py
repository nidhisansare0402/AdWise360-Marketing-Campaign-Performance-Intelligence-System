import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

os.makedirs('ml_models', exist_ok=True)

# 1. Load features
df = pd.read_csv('database/ml_campaign_features.csv')

# 2. Build X and y
feature_cols = [
    'total_impressions','total_clicks','total_conversions','total_spend','total_revenue',
    'avg_ctr','days_active','conv_rate','profit',
    'clicks_per_rupee','revenue_per_click','conversions_per_click','budget_utilization',
    'log_revenue','log_spend','log_profit'
]
feature_cols = [c for c in feature_cols if c in df.columns]
X = df[feature_cols]
y = df['avg_roi']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)

rf = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_split=4, min_samples_leaf=2, random_state=42, n_jobs=-1)
rf.fit(X_train,y_train)

preds = rf.predict(X_test)
print('R2 Score:', r2_score(y_test,preds))
print('MAE:', mean_absolute_error(y_test,preds))

joblib.dump(rf, 'ml_models/rf_tuned.pkl')
print('Saved tuned model to ml_models/rf_tuned.pkl')