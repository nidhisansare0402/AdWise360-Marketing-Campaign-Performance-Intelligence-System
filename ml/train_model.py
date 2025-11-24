import os
import json
import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# optional XGBoost import
try:
    from xgboost import XGBRegressor
    xgb_available = True
except Exception:
    xgb_available = False

FEATURES_CSV = "database/ml_campaign_features.csv"
if not os.path.exists(FEATURES_CSV):
    raise FileNotFoundError(f"{FEATURES_CSV} not found. Run scripts/build_ml_features.py first.")

df = pd.read_csv(FEATURES_CSV)

# 1) choose features automatically (drop identifiers + target)
drop_cols = {
    "campaign_id", "campaign_name", "platform_id", "objective", "region",
    "avg_roi", "predicted_roi"
}
feature_cols = [c for c in df.columns if c not in drop_cols]
X = df[feature_cols]

# 2) target (log-transform)
if "avg_roi" not in df.columns:
    raise ValueError("Target column 'avg_roi' not found in features CSV")
y = df["avg_roi"].astype(float)
y_log = np.log1p(y)   # target transform

# 3) train-test split (on rows)
X_train, X_test, y_train_log, y_test_log = train_test_split(X, y_log, test_size=0.2, random_state=42)

# 4) Train RandomForest (tuned baseline)
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train_log)

# Evaluate: predict in log space -> invert with expm1 to original scale
y_test_pred_log = rf.predict(X_test)
y_test_pred = np.expm1(y_test_pred_log)    # invert
y_test_actual = np.expm1(y_test_log)

rf_r2 = r2_score(y_test_actual, y_test_pred)
rf_mae = mean_absolute_error(y_test_actual, y_test_pred)
print(f"RandomForest (log-target) -> R2: {rf_r2:.4f}, MAE: {rf_mae:.4f}")

best_model = rf
best_score = rf_mae
best_name = "random_forest"

# 5) Optionally train XGBoost on log-target and compare (if available)
if xgb_available:
    xgb = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    xgb.fit(X_train, y_train_log)
    y_xgb_pred_log = xgb.predict(X_test)
    y_xgb_pred = np.expm1(y_xgb_pred_log)
    xgb_r2 = r2_score(y_test_actual, y_xgb_pred)
    xgb_mae = mean_absolute_error(y_test_actual, y_xgb_pred)
    print(f"XGBoost (log-target) -> R2: {xgb_r2:.4f}, MAE: {xgb_mae:.4f}")

    if xgb_mae < best_score:
        best_model = xgb
        best_score = xgb_mae
        best_name = "xgboost"

# 6) Save tuned model and metadata (use explicit names)
os.makedirs("ml_models", exist_ok=True)
model_path = os.path.join("ml_models", "rf_tuned.pkl")
joblib.dump(best_model, model_path)

meta = {
    "model_name": best_name,
    "model_file": os.path.basename(model_path),
    "trained_on_rows": int(len(df)),
    "feature_count": len(feature_cols),
    "feature_list": feature_cols,
    "target_transform": "log1p",
    "best_mae_on_original_scale": float(best_score)
}

# include raw metrics
meta["metrics"] = {"rf": {"r2_on_original": float(rf_r2), "mae_on_original": float(rf_mae)}}
if xgb_available:
    meta["metrics"]["xgboost"] = {"r2_on_original": float(xgb_r2), "mae_on_original": float(xgb_mae)}

with open(os.path.join("ml_models", "rf_tuned_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

print(f"Saved tuned model to {model_path}")
print("Saved metadata to ml_models/rf_tuned_meta.json")
