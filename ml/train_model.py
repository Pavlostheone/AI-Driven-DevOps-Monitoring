import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle
import os

# === Load labeled dataset ===
print("Loading dataset...")
df = pd.read_csv("ml/nab_labeled.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# === Feature engineering ===
# === Feature engineering ===
df["rolling_mean"] = df["cpu_percent"].rolling(window=12, min_periods=1).mean()
df["rolling_std"] = df["cpu_percent"].rolling(
    window=12, min_periods=1).std().fillna(0)
df["diff"] = df["cpu_percent"].diff().fillna(0)
df["rolling_max"] = df["cpu_percent"].rolling(window=12, min_periods=1).max()

# Time-based context features
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

features = [
    "cpu_percent",
    "rolling_mean",
    "rolling_std",
    "diff",
    "rolling_max",
    "hour",
    "day_of_week"]
X = df[features]

# === Train model ===
# contamination = how much of the data we expect to be anomalies
# 2 anomalies out of 4032 rows ≈ 0.0005
print("Training Isolation Forest...")
model = IsolationForest(
    n_estimators=100,
    contamination=0.0001,
    random_state=42
)
model.fit(X)

# === Evaluate against ground truth ===
df["prediction"] = model.predict(X)
# IsolationForest returns -1 for anomaly, 1 for normal
df["anomaly_predicted"] = (df["prediction"] == -1).astype(int)

print("\nEvaluation against ground truth:")
results = df[df["anomaly"] == 1][["timestamp",
                                  "cpu_percent", "anomaly", "anomaly_predicted"]]
print(results.to_string(index=False))

caught = (df["anomaly_predicted"] & df["anomaly"]).sum()
print(f"\nGround truth anomalies caught: {caught}/2")
print(f"Total flagged by model: {df['anomaly_predicted'].sum()}")

# === Save model ===
os.makedirs("ml", exist_ok=True)
with open("ml/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved to ml/model.pkl")
