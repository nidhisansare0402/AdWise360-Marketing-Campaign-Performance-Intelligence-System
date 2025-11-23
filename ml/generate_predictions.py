# ml/generate_predictions.py
import os
import json
import joblib
import pandas as pd
import sys
from pathlib import Path

# Ensure project root is on sys.path so app imports work
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.data_loader import load_to_df, create_campaign_features

def main():
    # 1. Load raw row-level data (ETL processed)
    df = load_to_df()

    # 2. Create campaign-level features (same function used for training)
    features_df = create_campaign_features(df)

    # 3. Load model + metadata
    model_path = os.path.join("ml_models", "rf_tuned.pkl")
    meta_path = os.path.join("ml_models", "rf_tuned_meta.json")
    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Model or metadata not found. Run ml/train_model.py first.")

    with open(meta_path, "r") as f:
        meta = json.load(f)

    feature_list = meta.get("feature_list", None)
    if feature_list is None:
        # fallback: pick sensible numeric columns
        drop_cols = {"campaign_id", "campaign_name", "platform_id", "objective", "region", "avg_roi", "predicted_roi"}
        feature_list = [c for c in features_df.columns if c not in drop_cols]

    # ensure platform/objective dummies are included (if present)
    # (metadata approach already includes dummies if present during training)
    model_cols = [c for c in feature_list if c in features_df.columns]

    if len(model_cols) == 0:
        raise RuntimeError("No model input columns found. Check feature_list and features_df.")

    # 4. Load model
    model = joblib.load(model_path)

    # 5. Predict
    X = features_df[model_cols]
    preds = model.predict(X)
    features_df["predicted_roi"] = preds

    # 6. Save predictions
    os.makedirs("database", exist_ok=True)
    out_path = os.path.join("database", "predictions_output.csv")
    features_df.to_csv(out_path, index=False)
    print("Saved predictions to", out_path)

if __name__ == "__main__":
    main()
