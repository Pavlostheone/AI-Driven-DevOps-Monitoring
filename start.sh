#!/bin/bash
echo "Starting port-forwards..."

# Kill any existing uvicorn processes first
cmd //c "taskkill /F /IM uvicorn.exe" 2>/dev/null || true

kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090 &
echo "Prometheus  → http://localhost:9090"
kubectl port-forward -n monitoring svc/postgres-postgresql 5432:5432 &
echo "PostgreSQL  → localhost:5432"
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
echo "Grafana     → http://localhost:3000"

echo ""
echo "All forwards running. Press Ctrl+C to stop all."

cd ~/DevOps-intelligence-Portfolio/01-AI-Driven-DevOps-Monitoring/Backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo "Backend     → http://localhost:8000"

cd ~/DevOps-intelligence-Portfolio/01-AI-Driven-DevOps-Monitoring
wait