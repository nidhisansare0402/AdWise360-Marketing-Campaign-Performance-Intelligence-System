import joblib
import pandas as pd

model = joblib.load("ml_models/roi_model.pkl")

columns = [
    "total_impressions","total_clicks","total_conversions",
    "total_spend","total_revenue","avg_ctr",
    "days_active","conv_rate","profit"
]

importances = model.feature_importances_
df_importance = pd.DataFrame({
    "feature": columns,
    "importance": importances
}).sort_values("importance", ascending=False)

print("\n===== FEATURE IMPORTANCE =====")
print(df_importance.to_string(index=False))
