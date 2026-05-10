from fastapi import FastAPI, Query
import psycopg2
import os
from app.routes.prediction import router as prediction_router


app = FastAPI(title="DevOps AI Monitor")
app.include_router(prediction_router)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "devops123")
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
def root():
    return {"message": "Backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics/history")
def metrics_history(limit: int = Query(default=50, le=500)):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT timestamp, cpu_percent, memory_percent, pod_count
            FROM cluster_metrics
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    conn.close()

    return [
        {
            "timestamp": str(row[0]),
            "cpu_percent": row[1],
            "memory_percent": row[2],
            "pod_count": row[3]
        }
        for row in rows
    ]