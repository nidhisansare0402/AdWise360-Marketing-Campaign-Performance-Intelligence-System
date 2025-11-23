import joblib, pandas as pd, os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

df = pd.read_csv("database/ml_campaign_features.csv")
# build feature list same as train_model used
drop_cols = {'campaign_id','campaign_name','platform_id','objective','region','avg_roi','predicted_roi'}
X = df[[c for c in df.columns if c not in drop_cols]]
y = df['avg_roi']

param_dist = {
    "n_estimators": [100,200,300,500],
    "max_depth": [6,8,12,16,None],
    "min_samples_split": [2,4,6,8],
    "min_samples_leaf": [1,2,4,6],
    "max_features": ['auto','sqrt','log2']
}

rf = RandomForestRegressor(random_state=42, n_jobs=-1)
rs = RandomizedSearchCV(rf, param_distributions=param_dist, n_iter=30, scoring='neg_mean_absolute_error', cv=4, verbose=2, random_state=42)
rs.fit(X, y)

print("Best params:", rs.best_params_)
print("Best MAE (cv):", -rs.best_score_)

os.makedirs("ml_models", exist_ok=True)
joblib.dump(rs.best_estimator_, "ml_models/rf_tuned.pkl")
print("Saved tuned rf to ml_models/rf_tuned.pkl")
