# AI-Driven DevOps Monitoring
### Proactive Incident Management with Kubernetes, Prometheus and AI Anomaly Detection

**Author:** Daniel Pavlos | Class: DOE24  
**Type:** Thesis Project — Individual  
**Status:** 🟡 In Progress

---

## Overview

Modern DevOps environments run on distributed systems, often in Kubernetes and cloud platforms. Traditional monitoring tools like Prometheus and Grafana are powerful but rely on static thresholds and manually configured alerts — leading to alert fatigue, reactive incident handling, and missed complex failure patterns.

This project investigates how AI can be integrated into DevOps monitoring to create a more proactive and intelligent system. The goal is not to replace DevOps decision-making with AI, but to improve the signal-to-noise ratio so engineers focus on what actually matters.

---

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Kubernetes (Docker Desktop) |
| Metrics Collection | Prometheus |
| Visualization | Grafana |
| AI / Anomaly Detection | Python — Isolation Forest |
| Model Evaluation | Isolation Forest vs Local Outlier Factor |
| Dataset | NAB (Numenta Anomaly Benchmark) |
| Backend API | FastAPI + Uvicorn |
| Database | PostgreSQL |
| CI/CD | GitHub Actions |
| Package Management | Helm |

---

## Project Structure

```
AI-Driven-DevOps-Monitoring/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── routes/
│       │   └── prediction.py        # /predict endpoint
│       ├── services/
│       │   └── ml_model.py          # model loading, rolling window, inference
│       ├── db/
│       ├── schemas/
│       │   └── metric_schema.py     # Pydantic input/output models
│       └── utils/
│
├── ml/
│   ├── prepare_dataset.py           # loads NAB CSV, labels anomalies
│   ├── train_model.py               # trains Isolation Forest, saves model.pkl
│   ├── evaluate_model.py            # compares Isolation Forest vs LOF
│   ├── nab_labeled.csv              # prepared dataset (4032 rows, 2 anomalies)
│   └── model.pkl                    # trained model (Isolation Forest)
│
├── scripts/
│   ├── collect_pod_metrics.sh
│   ├── collect_docker.sh
│   ├── healthcheck.sh
│   ├── config.env
│   ├── common.sh
│   ├── utils.sh
│   └── legacy/
│       ├── collect_cpu.sh
│       ├── collect_memory.sh
│       ├── collect_disk.sh
│       ├── collect_network.sh
│       ├── collect_processes.sh
│       └── collect_metrics.sh
│
├── docs/
│   ├── architecture.md
│   ├── command_log.md
│   └── report-notes.md              # ML findings and thesis write-up
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── setup.sh                         # installs all Python dependencies
└── README.md
```

---

## Getting Started

### Prerequisites
- Docker Desktop with Kubernetes enabled
- Helm v3+
- kubectl
- Python 3.x
- Git Bash (Windows)

### 1. Install dependencies
```bash
bash setup.sh
```

### 2. Prepare the ML dataset
```bash
python ml/prepare_dataset.py
```

### 3. Train the model
```bash
python ml/train_model.py
```

### 4. Evaluate the model (Isolation Forest vs LOF)
```bash
python ml/evaluate_model.py
```

### 5. Verify cluster is running
```bash
kubectl get nodes
```

### 6. Deploy Prometheus + Grafana
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 7. Start all services
```bash
bash start.sh
```

This forwards:
- Prometheus → http://localhost:9090
- Grafana → http://localhost:3000
- PostgreSQL → localhost:5432
- Backend API → http://localhost:8000

### 8. Test the predict endpoint
```bash
# Normal reading
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_percent": 0.13, "timestamp": "2014-02-26T21:50:00"}'

# Anomalous spike
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_percent": 2.344, "timestamp": "2014-02-26T22:05:00"}'
```

---

## AI Anomaly Detection — Results

**Dataset:** NAB `ec2_cpu_utilization_24ae8d.csv`  
**Ground truth:** 2 anomalies manually verified by Numenta researchers  
**Rows:** 4,032 at 5-minute intervals

| Model | Flagged | Caught | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Isolation Forest | 4 | 1 / 2 | 0.25 | 0.50 | 0.33 |
| Local Outlier Factor | 4 | 1 / 2 | 0.25 | 0.50 | 0.33 |

Both models correctly detected the point anomaly at `2014-02-26 22:05:00` (CPU spike to 2.344%, approximately 17x above baseline). The contextual anomaly at `2014-02-27 17:15:00` (0.602%) was missed by both, consistent with known limitations of unsupervised density-based methods on contextual anomalies without temporal sequence modelling.

Isolation Forest was selected for API integration due to lower computational complexity and support for online inference. The `/predict` endpoint uses a 12-point rolling window to compute real-time features, replicating the statistical context used during training.

See `docs/report-notes.md` for full findings and thesis write-up.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Service status |
| GET | `/metrics/history` | Recent metrics from database |
| POST | `/predict` | Run anomaly detection on a CPU reading |

### /predict — Request
```json
{
  "cpu_percent": 2.344,
  "timestamp": "2014-02-26T22:05:00"
}
```

### /predict — Response
```json
{
  "timestamp": "2014-02-26T22:05:00",
  "cpu_percent": 2.344,
  "anomaly": true,
  "message": "ANOMALY DETECTED"
}
```

---

## Thesis Phases

- [x] Phase 1 — Research
- [x] Phase 2 — Architecture Design
- [x] Phase 3 — Kubernetes + Prometheus + Grafana Setup
- [x] Phase 4 — AI Anomaly Detection (Isolation Forest on NAB dataset)
- [ ] Phase 5 — Platform Engineering Layer
- [ ] Phase 6 — Evaluation (alert count before vs after AI)

---

## Key Design Decisions

**Why Kubernetes over a custom backend?**  
Kubernetes is the industry standard for container orchestration. Building the monitoring system natively in Kubernetes means the architecture reflects real-world DevOps practice rather than a simplified standalone backend.

**Why Prometheus over custom bash collection?**  
Prometheus natively scrapes cluster metrics with higher reliability, lower overhead, and better data quality than custom shell scripts. Shell-based collectors were prototyped early in the project and archived in `scripts/legacy/` once Prometheus was deployed.

**Why Isolation Forest for anomaly detection?**  
Isolation Forest is an unsupervised algorithm well suited to anomaly detection on time-series metric data. It does not require labelled training data from your own system, making it practical for a project of this scope and timeline.

**Why compare with Local Outlier Factor?**  
LOF was evaluated as a theoretically stronger candidate for contextual anomalies due to its density-based neighbourhood scoring. Both models produced identical results, which strengthens the conclusion that the missed anomaly represents a genuine limitation of unsupervised point-based methods rather than a model selection issue.

**Why a rolling window in the predict endpoint?**  
Single-point inference without context produces poor results because features like rolling mean and standard deviation are meaningless on isolated readings. A 12-point in-memory deque replicates the statistical context the model was trained on.

---

## Portfolio Value

This project is presentable as:
- A working GitHub repository with real Kubernetes infrastructure
- A live or recorded demo
- A case study: *"Reducing Alert Fatigue Using AI in DevOps"*
