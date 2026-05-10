import pandas as pd
import json
import os

# === Config === #
DATA_FILE = "ml/NAB/NAB-master/data/realAWSCloudwatch/ec2_cpu_utilization_24ae8d.csv"
LABELS_FILE = "ml/NAB/NAB-master/labels/combined_labels.json"
DATASET_KEY = "realAWSCloudwatch/ec2_cpu_utilization_24ae8d.csv"
OUTPUT_FILE = "ml/nab_labeled.csv"

def main():
    # Load the metric data
    print("Loading dataset...")
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])

    # Load the labels
    with open(LABELS_FILE) as f:
        labels = json.load(f)

    # Get anomaly timestamps for this file
    anomaly_timestamps = pd.to_datetime(labels[DATASET_KEY])
    print(f"Anomaly timestamps: {list(anomaly_timestamps)}")

    # Mark each row as anomaly (1) or normal (0)
    df["anomaly"] = df["timestamp"].isin(anomaly_timestamps).astype(int)

    # Rename value column to match our cluster data
    df.rename(columns={"value": "cpu_percent"}, inplace=True)

    # Save labeled dataset
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(df)} rows to {OUTPUT_FILE}")
    print(f"Anomalies labeled: {df['anomaly'].sum()}")
    print(f"Normal rows: {(df['anomaly'] == 0).sum()}")
    print("\nSample rows around first anomaly:")
    first = anomaly_timestamps[0]
    mask = (df["timestamp"] >= first - pd.Timedelta(minutes=15)) & \
           (df["timestamp"] <= first + pd.Timedelta(minutes=15))
    print(df[mask].to_string(index=False))

if __name__ == "__main__":
    main()
