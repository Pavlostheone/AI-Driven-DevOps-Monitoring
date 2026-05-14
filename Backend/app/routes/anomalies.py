from fastapi import APIRouter, Query
import psycopg2
import os

router = APIRouter()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "devops123")
}


@router.get("/anomalies")
def get_anomalies(limit: int = Query(default=50, le=500), only_anomalies: bool = False):
    conn = psycopg2.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        if only_anomalies:
            cur.execute("""
                SELECT timestamp, cpu_percent, anomaly, message, created_at
                FROM anomaly_results
                WHERE anomaly = TRUE
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
        else:
            cur.execute("""
                SELECT timestamp, cpu_percent, anomaly, message, created_at
                FROM anomaly_results
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
        rows = cur.fetchall()
    conn.close()

    return [
        {
            "timestamp": str(row[0]),
            "cpu_percent": row[1],
            "anomaly": row[2],
            "message": row[3],
            "created_at": str(row[4])
        }
        for row in rows
    ]