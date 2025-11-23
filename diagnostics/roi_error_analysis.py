import pandas as pd

df = pd.read_csv("database/predictions_output.csv")

# Calculate errors
df['abs_error'] = (df['predicted_roi'] - df['avg_roi']).abs()
df['pct_error'] = df['abs_error'] / df['avg_roi'].replace(0, 1) * 100

print("\n===== BASIC ERROR METRICS =====")
print("Mean Absolute Error (ROI points):", df['abs_error'].mean())
print("Median Absolute Error:", df['abs_error'].median())
print("Mean % Error:", df['pct_error'].mean())
print("Median % Error:", df['pct_error'].median())

print("\n===== WORST 10 CAMPAIGNS =====")
worst = df.sort_values('abs_error', ascending=False).head(5)
print(worst[['campaign_id', 'campaign_name', 'avg_roi', 'predicted_roi', 'abs_error', 'pct_error']].to_string(index=False))
