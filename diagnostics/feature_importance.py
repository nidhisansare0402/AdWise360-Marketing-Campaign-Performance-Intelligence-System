import joblib
import pandas as pd
import os
import sys
from pathlib import Path

# Make sure script can import project code if needed
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

MODEL_PATH = "ml_models/rf_tuned.pkl"
FEATURES_CSV = "database/ml_campaign_features.csv"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train model first.")

# Load model
model = joblib.load(MODEL_PATH)

# Try to get feature names from the model (sklearn exposes .feature_names_in_ for most estimators)
if hasattr(model, "feature_names_in_"):
    feature_names = list(model.feature_names_in_)
else:
    # fallback: load features CSV and infer numeric cols used for training (drop id/label cols)
    if not os.path.exists(FEATURES_CSV):
        raise FileNotFoundError(f"Features CSV not found at {FEATURES_CSV}. Regenerate features first.")
    df = pd.read_csv(FEATURES_CSV)
    # Heuristics: drop obvious non-feature columns
    drop_cols = {'campaign_id','campaign_name','platform_id','objective','region','avg_roi','predicted_roi'}
    # preserve order
    feature_names = [c for c in df.columns if c not in drop_cols]

# Get importances (works for sklearn tree-based models)
if hasattr(model, "feature_importances_"):
    importances = list(model.feature_importances_)
elif hasattr(model, "coef_"):
    # linear model case
    importances = list(abs(model.coef_).ravel())
else:
    raise RuntimeError("Model does not expose feature importances or coefficients.")

# Defensive sanity check
if len(importances) != len(feature_names):
    print("WARNING: number of importance values does not match number of feature names.")
    print(f"len(importances) = {len(importances)}, len(feature_names) = {len(feature_names)}")
    # Try to truncate/extend safely
    min_len = min(len(importances), len(feature_names))
    importances = importances[:min_len]
    feature_names = feature_names[:min_len]

# Build dataframe and display
fi_df = pd.DataFrame({"feature": feature_names, "importance": importances})
fi_df = fi_df.sort_values("importance", ascending=False).reset_index(drop=True)

print("\n===== FEATURE IMPORTANCE =====")
print(fi_df.to_string(index=False))

# Optionally save to diagnostics folder
out_dir = Path("diagnostics")
out_dir.mkdir(exist_ok=True)
fi_df.to_csv(out_dir / "feature_importance.csv", index=False)
print(f"\nSaved feature importance CSV to {out_dir / 'feature_importance.csv'}")
