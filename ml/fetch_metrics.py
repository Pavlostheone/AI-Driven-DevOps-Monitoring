import requests
import pandas as pd
from datetime import datetime, timedelta

# Prometheus URL - port-forward must be running
PROMETHEUS_URL = "http://localhost:9090"

def query_prometheus(query):
    """Query Prometheus and return result as a list of (timestamp, value) tuples."""
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query_range",
        params={
            "query": query,
            "start": (datetime.now() - timedelta(hours=1)).timestamp(),
            "end": datetime.now().timestamp(),
            "step": "30s"
        }
    )
    results = response.json().get("data", {}).get("result", [])
    return results

def extract_average(results):
    """Average across all nodes per timestamp."""
    data = {}
    for series in results:
        for timestamp, value in series["values"]:
            if timestamp not in data:
                data[timestamp] = []
            data[timestamp].append(float(value))
    return {ts: sum(vals) / len(vals) for ts, vals in data.items()}

def to_df(data, col_name):
    rows = [
        {
            "timestamp": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            col_name: round(val, 2)
        }
        for ts, val in data.items()
    ]
    return pd.DataFrame(rows)

def main():
    print("Fetching CPU metrics...")
    cpu_raw = query_prometheus(
        '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    )

    print("Fetching memory metrics...")
    memory_raw = query_prometheus(
        "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
    )

    print("Fetching pod count...")
    pod_raw = query_prometheus(
        "count by (node) (kube_pod_info)"
    )

    cpu_data = extract_average(cpu_raw)
    memory_data = extract_average(memory_raw)
    pod_data = extract_average(pod_raw)

    df_cpu = to_df(cpu_data, "cpu_percent")
    df_mem = to_df(memory_data, "memory_percent")
    df_pod = to_df(pod_data, "pod_count")

    df = df_cpu.merge(df_mem, on="timestamp", how="outer") \
               .merge(df_pod, on="timestamp", how="outer") \
               .sort_values("timestamp") \
               .ffill()

    df.to_csv("ml/cluster_metrics.csv", index=False)

    print(f"\nSaved {len(df)} rows to ml/cluster_metrics.csv")
    print(df.head(10))

if __name__ == "__main__":
    main()
