import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.etl import get_cached_data
from app.data_loader import create_campaign_features

def main():
    print("Loading row-level joined dataset...")
    df = get_cached_data()
    print("Building ML features...")
    features = create_campaign_features(df)
    features.to_csv("database/ml_campaign_features.csv", index=False)
    print("Saved features to database/ml_campaign_features.csv")
    print("Rows:", len(features))

if __name__ == "__main__":
    main()
