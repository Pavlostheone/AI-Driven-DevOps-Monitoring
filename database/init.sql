CREATE TABLE IF NOT EXISTS anomaly_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    cpu_percent FLOAT NOT NULL,
    anomaly BOOLEAN NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);