import os
import joblib
import pandas as pd
from app.data_loader import load_to_df, create_campaign_features

def main():
    # 1. Load transformed row-level df (with CTR/ROI etc)
    df = load_to_df()

    # 2. Build features (ensures engineered features are created)
    features_df = create_campaign_features(df)

    # 3. Load best model
    model_path = os.path.join("ml_models", "best_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Run ml/train_model.py first.")
    model = joblib.load(model_path)

    # 4. Prepare model input columns (match train_model)
    # Create the same list you used when training
    model_cols = [
        "total_impressions","total_clicks","total_conversions",
        "total_spend","total_revenue","avg_ctr","days_active",
        "conv_rate","profit",
        "clicks_per_rupee","revenue_per_click","conversions_per_click",
        "budget_utilization","log_revenue","log_spend","log_profit"
    ]
    # include platform/objective dummies automatically
    for c in features_df.columns:
        if c.startswith("platform_") or c.startswith("obj_"):
            model_cols.append(c)

    model_cols = [c for c in model_cols if c in features_df.columns]
    X = features_df[model_cols]

    features_df['predicted_roi'] = model.predict(X)

    os.makedirs("database", exist_ok=True)
    out_path = os.path.join("database", "predictions_output.csv")
    features_df.to_csv(out_path, index=False)
    print("Saved predictions to", out_path)

if __name__ == "__main__":
    main()
