import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import precision_score, recall_score, f1_score

# === Load dataset ===
print("Loading dataset...")
df = pd.read_csv("ml/nab_labeled.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# === Feature engineering ===
df["rolling_mean"] = df["cpu_percent"].rolling(window=12, min_periods=1).mean()
df["rolling_std"] = df["cpu_percent"].rolling(
    window=12, min_periods=1).std().fillna(0)
df["diff"] = df["cpu_percent"].diff().fillna(0)
df["rolling_max"] = df["cpu_percent"].rolling(window=12, min_periods=1).max()
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
y_true = df["anomaly"]

# === Model 1: Isolation Forest ===
print("\n--- Isolation Forest ---")
iso = IsolationForest(n_estimators=100, contamination=0.001, random_state=42)
iso.fit(X)
iso_preds = (iso.predict(X) == -1).astype(int)

print(f"Anomalies flagged: {iso_preds.sum()}")
print(f"Precision: {precision_score(y_true, iso_preds, zero_division=0):.2f}")
print(f"Recall:    {recall_score(y_true, iso_preds, zero_division=0):.2f}")
print(f"F1 Score:  {f1_score(y_true, iso_preds, zero_division=0):.2f}")

# === Model 2: Local Outlier Factor ===
print("\n--- Local Outlier Factor ---")
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.001)
lof_preds = (lof.fit_predict(X) == -1).astype(int)

print(f"Anomalies flagged: {lof_preds.sum()}")
print(f"Precision: {precision_score(y_true, lof_preds, zero_division=0):.2f}")
print(f"Recall:    {recall_score(y_true, lof_preds, zero_division=0):.2f}")
print(f"F1 Score:  {f1_score(y_true, lof_preds, zero_division=0):.2f}")

# === Ground truth comparison ===
print("\n--- Ground Truth Breakdown ---")
df["iso_predicted"] = iso_preds
df["lof_predicted"] = lof_preds

results = df[df["anomaly"] == 1][["timestamp",
                                  "cpu_percent", "iso_predicted", "lof_predicted"]]
print(results.to_string(index=False))

# === Save best model ===
# We'll compare F1 scores and save the winner
iso_f1 = f1_score(y_true, iso_preds, zero_division=0)
lof_f1 = f1_score(y_true, lof_preds, zero_division=0)

best_model_name = "IsolationForest" if iso_f1 >= lof_f1 else "LOF"
best_model = iso if iso_f1 >= lof_f1 else lof

print(f"\nBest model by F1: {best_model_name}")

with open("ml/model.pkl", "wb") as f:
    pickle.dump(best_model, f)

print("Best model saved to ml/model.pkl")
