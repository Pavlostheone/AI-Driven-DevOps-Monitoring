import requests
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "devops123")
}

def query_prometheus(query):
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query_range",
        params={
            "query": query,
            "start": (datetime.now() - timedelta(hours=1)).timestamp(),
            "end": datetime.now().timestamp(),
            "step": "30s"
        }
    )
    return response.json().get("data", {}).get("result", [])

def extract_average(results):
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

def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cluster_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP UNIQUE,
                cpu_percent FLOAT,
                memory_percent FLOAT,
                pod_count FLOAT
            )
        """)
        conn.commit()
    print("Database table ready.")

def save_to_db(conn, df):
    inserted = 0
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO cluster_metrics (timestamp, cpu_percent, memory_percent, pod_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING
            """, (row["timestamp"], row["cpu_percent"], row["memory_percent"], row["pod_count"]))
            if cur.rowcount > 0:
                inserted += 1
        conn.commit()
    print(f"Inserted {inserted} new rows into database.")

def main():
    print("Fetching CPU metrics...")
    cpu_data = extract_average(query_prometheus(
        '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
    ))

    print("Fetching memory metrics...")
    memory_data = extract_average(query_prometheus(
        "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
    ))

    print("Fetching pod count...")
    pod_data = extract_average(query_prometheus(
        "count by (node) (kube_pod_info)"
    ))

    df = to_df(cpu_data, "cpu_percent") \
        .merge(to_df(memory_data, "memory_percent"), on="timestamp", how="outer") \
        .merge(to_df(pod_data, "pod_count"), on="timestamp", how="outer") \
        .sort_values("timestamp") \
        .ffill()

    print(f"Fetched {len(df)} rows.")

    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    setup_db(conn)
    save_to_db(conn, df)
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()