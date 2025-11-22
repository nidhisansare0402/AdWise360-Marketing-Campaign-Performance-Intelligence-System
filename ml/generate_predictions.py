import os
import joblib
import pandas as pd
from app.data_loader import load_to_df, create_campaign_features
# we use load_to_df so KPIs (CTR, ROI, ...) are already computed

def main():
    # 1. Load the fully transformed DataFrame (extract+transform)
    df = load_to_df()
    print("Loaded transformed df rows:", len(df))
    print("Columns available:", list(df.columns))

    # 2. Build campaign-level features (same logic as training)
    features_df = create_campaign_features(df)

    # 3. Load model
    model_path = os.path.join("ml_models", "roi_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Train model first (ml/train_model.py).")

    model = joblib.load(model_path)

    # 4. Prepare model input (must match training features)
    feature_cols = [
        "total_impressions",
        "total_clicks",
        "total_conversions",
        "total_spend",
        "total_revenue",
        "avg_ctr",
        "days_active",
        "conv_rate",
        "profit"
    ]
    # defensive: ensure columns exist
    missing = [c for c in feature_cols if c not in features_df.columns]
    if missing:
        raise RuntimeError("Missing feature columns before prediction: " + ", ".join(missing))

    X = features_df[feature_cols]

    # 5. Predict ROI
    features_df["predicted_roi"] = model.predict(X)

    # 6. Save predictions
    os.makedirs("database", exist_ok=True)
    out_path = os.path.join("database", "predictions_output.csv")
    features_df.to_csv(out_path, index=False)
    print("Predictions saved to", out_path)

if __name__ == "__main__":
    main()
