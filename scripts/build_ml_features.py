import sys
from pathlib import Path

# Project root = parent of scripts/ folder
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.data_loader import load_to_df, create_campaign_features
import os

def main():
    df = load_to_df()
    features = create_campaign_features(df)
    os.makedirs("database", exist_ok=True)
    out_path = os.path.join("database", "ml_campaign_features.csv")
    features.to_csv(out_path, index=False)
    print("Wrote", out_path, "rows:", len(features), "cols:", len(features.columns))

if __name__ == "__main__":
    main()
