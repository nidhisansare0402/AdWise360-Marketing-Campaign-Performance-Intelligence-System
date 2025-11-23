import pandas as pd

df = pd.read_csv("database/predictions_output.csv")

df['abs_error'] = (df['predicted_roi'] - df['avg_roi']).abs()
df['pct_error'] = df['abs_error'] / df['avg_roi'].replace(0, 1) * 100

grouped = df.groupby('platform_id').agg(
    actual_mean=('avg_roi','mean'),
    predicted_mean=('predicted_roi','mean'),
    mae=('abs_error','mean'),
    median_pct_err=('pct_error','median')
).reset_index()

print("\n===== PLATFORM-WISE BIAS =====")
print(grouped.to_string(index=False))
