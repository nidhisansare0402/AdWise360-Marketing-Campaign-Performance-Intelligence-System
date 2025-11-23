import os
import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# try import xgboost, if not present instruct user
try:
    from xgboost import XGBRegressor
    xgb_available = True
except Exception:
    xgb_available = False

# 1. Load features
df = pd.read_csv("database/ml_campaign_features.csv")

# 2. Define features and target
# Add the new engineered features here — ensure they exist in df
feature_cols = [
    "total_impressions", "total_clicks", "total_conversions",
    "total_spend", "total_revenue", "avg_ctr", "days_active",
    "conv_rate", "profit",
    # engineered:
    "clicks_per_rupee", "revenue_per_click", "conversions_per_click",
    "budget_utilization", "log_revenue", "log_spend", "log_profit"
]

# include any platform/objective dummies present
for c in df.columns:
    if c.startswith("platform_") or c.startswith("obj_"):
        feature_cols.append(c)

# ensure feature cols are available
feature_cols = [c for c in feature_cols if c in df.columns]

X = df[feature_cols]
y = df["avg_roi"]

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. RandomForest (tuned baseline)
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)
rf_preds = rf.predict(X_test)
rf_r2 = r2_score(y_test, rf_preds)
rf_mae = mean_absolute_error(y_test, rf_preds)
print(f"RandomForest -> R2: {rf_r2:.4f}, MAE: {rf_mae:.4f}")

best_model = rf
best_score = rf_mae
best_name = "random_forest"

# 5. XGBoost (if available) — often improves results
if xgb_available:
    xgb = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs= -1
    )
    xgb.fit(X_train, y_train)
    xgb_preds = xgb.predict(X_test)
    xgb_r2 = r2_score(y_test, xgb_preds)
    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    print(f"XGBoost     -> R2: {xgb_r2:.4f}, MAE: {xgb_mae:.4f}")

    if xgb_mae < best_score:
        best_model = xgb
        best_score = xgb_mae
        best_name = "xgboost"

# 6. Save best model
os.makedirs("ml_models", exist_ok=True)
model_path = os.path.join("ml_models", "best_model.pkl")
joblib.dump(best_model, model_path)
print(f"Saved best model ({best_name}) to {model_path}")
