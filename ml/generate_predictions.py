import os
import json
import joblib
import pandas as pd
import sys
from pathlib import Path
import numpy as np

# ensure project root on sys.path for app imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.data_loader import load_to_df, create_campaign_features

def main():
    # 1) load row-level ETL data
    df = load_to_df()

    # 2) create campaign-level features
    features_df = create_campaign_features(df)

    # 3) load tuned model + metadata
    model_path = os.path.join("ml_models", "rf_tuned.pkl")
    meta_path = os.path.join("ml_models", "rf_tuned_meta.json")
    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Model or metadata not found. Run ml/train_model.py first.")

    with open(meta_path, "r") as f:
        meta = json.load(f)

    feature_list = meta.get("feature_list", None)
    target_transform = meta.get("target_transform", None)

    # 4) prepare model cols (fall back if metadata missing)
    drop_cols = {"campaign_id", "campaign_name", "platform_id", "objective", "region", "avg_roi", "predicted_roi"}
    if feature_list is None:
        model_cols = [c for c in features_df.columns if c not in drop_cols]
    else:
        model_cols = [c for c in feature_list if c in features_df.columns]

    if len(model_cols) == 0:
        raise RuntimeError("No model input columns found. Check feature_list and features_df.")

    X = features_df[model_cols]

    # 5) load model and predict in model's target space
    model = joblib.load(model_path)

    preds_model_space = model.predict(X)

    # 6) invert target transform if required
    if target_transform == "log1p":
        preds_original = np.expm1(preds_model_space)
    else:
        preds_original = preds_model_space

    features_df["predicted_roi"] = preds_original

    # 7) save predictions
    os.makedirs("database", exist_ok=True)
    out_path = os.path.join("database", "predictions_output.csv")
    features_df.to_csv(out_path, index=False)
    print("Saved predictions to", out_path)

if __name__ == "__main__":
    main()
