import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

# 1. Load features
df = pd.read_csv("database/ml_campaign_features.csv")

# 2. Select features (X) and target (y)
# Remove non-numeric identifiers
X = df[[
    "total_impressions",
    "total_clicks",
    "total_conversions",
    "total_spend",
    "total_revenue",
    "avg_ctr",
    "days_active",
    "conv_rate",
    "profit"
]]

y = df["avg_roi"]     # PREDICT ROI

# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

# 5. Train
model.fit(X_train, y_train)

# 6. Evaluate
preds = model.predict(X_test)

print("R2 Score:", r2_score(y_test, preds))
print("MAE:", mean_absolute_error(y_test, preds))

# 7. Save model
os.makedirs("ml_models", exist_ok=True)
joblib.dump(model, "ml_models/roi_model.pkl")

print("Model saved as ml_models/roi_model.pkl")
