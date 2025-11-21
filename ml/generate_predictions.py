import pandas as pd
import joblib
from app.data_loader import create_campaign_features
from app.db_connection import get_db_connection   # if you need DB engine
from sqlalchemy import text

# 1. Load full dataset (not filtered)
engine = get_db_connection()
df = pd.read_sql(text("SELECT * FROM metrics m JOIN campaigns c ON m.campaign_id=c.campaign_id;"), engine)

# 2. Recreate ML features
features_df = create_campaign_features(df)

# 3. Load model
model = joblib.load("ml_models/roi_model.pkl")

# 4. Predict ROI
model_input = features_df[[
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

features_df["predicted_roi"] = model.predict(model_input)

# 5. Save predictions to CSV
features_df.to_csv("database/predictions_output.csv", index=False)

print("Predictions saved to database/predictions_output.csv")
