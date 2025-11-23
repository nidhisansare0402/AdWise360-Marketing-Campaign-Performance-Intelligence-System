import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("database/predictions_output.csv")

plt.figure(figsize=(8,6))
plt.scatter(df['avg_roi'], df['predicted_roi'], alpha=0.6)
plt.plot([df['avg_roi'].min(), df['avg_roi'].max()],
         [df['avg_roi'].min(), df['avg_roi'].max()], 
         'r--', label="Perfect Prediction")

plt.xlabel("Actual ROI")
plt.ylabel("Predicted ROI")
plt.title("Predicted vs Actual ROI")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
