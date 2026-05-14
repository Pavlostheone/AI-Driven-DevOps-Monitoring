import requests
import psycopg2
from datetime import datetime, timezone
import time
import os

# === Config ===
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
PREDICT_URL = os.getenv("PREDICT_URL", "http://localhost:8000/predict")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "devops123")
}

PROMQL = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'


def fetch_cpu_from_prometheus() -> float:
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": PROMQL},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("data", {}).get("result", [])
    if not results:
        raise ValueError("No CPU data returned from Prometheus")
    return float(results[0]["value"][1])


def send_to_predict(cpu_percent: float, timestamp: datetime) -> dict:
    payload = {
        "cpu_percent": cpu_percent,
        "timestamp": timestamp.isoformat()
    }
    response = requests.post(PREDICT_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def store_result(result: dict):
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO anomaly_results (timestamp, cpu_percent, anomaly, message)
            VALUES (%s, %s, %s, %s)
        """, (
            result["timestamp"],
            result["cpu_percent"],
            result["anomaly"],
            result["message"]
        ))
    conn.commit()
    conn.close()


def run():
    print(f"Anomaly detector started. Polling every {POLL_INTERVAL}s")
    print(f"Prometheus: {PROMETHEUS_URL}")
    print(f"Predict:    {PREDICT_URL}")

    while True:
        try:
            timestamp = datetime.now(timezone.utc)
            cpu = fetch_cpu_from_prometheus()
            result = send_to_predict(cpu, timestamp)
            store_result(result)

            status = "🚨 ANOMALY" if result["anomaly"] else "✅ Normal"
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} | CPU: {cpu:.3f}% | {status}")

        except Exception as e:
            print(f"ERROR: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()