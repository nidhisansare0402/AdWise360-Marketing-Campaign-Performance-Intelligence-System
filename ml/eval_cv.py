import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("database/ml_campaign_features.csv")
drop_cols = {"campaign_id","campaign_name","platform_id","objective","region","avg_roi","predicted_roi"}
X = df[[c for c in df.columns if c not in drop_cols]]
y = df["avg_roi"]

mae_scorer = make_scorer(mean_absolute_error, greater_is_better=False)

# 1) CV on current (untuned) RF baseline (match your train_model config)
rf = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_split=4, min_samples_leaf=2, random_state=42, n_jobs=-1)
scores = cross_val_score(rf, X, y, cv=5, scoring=mae_scorer, n_jobs=-1)
print("RF baseline CV MAE (5-fold):", -scores.mean(), "±", scores.std())

# 2) CV on tuned model from file (if exists)
try:
    tuned = joblib.load("ml_models/rf_tuned.pkl")
    scores2 = cross_val_score(tuned, X, y, cv=5, scoring=mae_scorer, n_jobs=-1)
    print("RF tuned CV MAE (5-fold):", -scores2.mean(), "±", scores2.std())
except FileNotFoundError:
    print("rf_tuned.pkl not found. Skip tuned eval.")

# based on results model needs structural improvements, NOT hyperparameter tweaks
# Hyperparameter tuning didn’t improve MAE because the underlying distribution was unstable.