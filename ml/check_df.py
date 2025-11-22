# ml/check_df.py
from app.data_loader import load_to_df
df = load_to_df()
print("Rows:", len(df))
print("Columns:", list(df.columns))
print(df.head().to_string())
print(df[['CTR','ROI']].head().to_string())
