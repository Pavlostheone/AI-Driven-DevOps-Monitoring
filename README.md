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
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Package Management | Helm |

---

## Project Structure

```
AI-Driven-DevOps-Monitoring/
│
├── Backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, all routes registered here
│   │   ├── routes/
│   │   │   ├── prediction.py        # POST /predict — runs Isolation Forest
│   │   │   └── anomalies.py         # GET /anomalies — queries stored results
│   │   ├── services/
│   │   │   └── ml_model.py          # Model loading, rolling window, inference
│   │   ├── schemas/
│   │   │   └── metric_schema.py     # Pydantic input/output models
│   │   ├── db/
│   │   └── utils/
│   ├── Dockerfile
│   └── requirements.txt
│
├── ml/
│   ├── prepare_dataset.py           # Loads NAB CSV, labels ground truth anomalies
│   ├── train_model.py               # Trains Isolation Forest, saves model.pkl
│   ├── evaluate_model.py            # Compares Isolation Forest vs LOF
│   ├── anomaly_detector.py          # Polls Prometheus → /predict → PostgreSQL
│   ├── fetch_metrics.py             # Fetches live metrics from Prometheus
│   ├── nab_labeled.csv              # Prepared dataset (4032 rows, 2 anomalies)
│   └── model.pkl                    # Trained Isolation Forest model
│
├── scripts/
│   ├── collect_pod_metrics.sh
│   ├── collect_docker.sh
│   ├── healthcheck.sh
│   ├── config.env
│   ├── common.sh
│   ├── utils.sh
│   └── legacy/                      # Replaced by Prometheus native collection
│       ├── collect_cpu.sh
│       ├── collect_memory.sh
│       ├── collect_disk.sh
│       ├── collect_network.sh
│       ├── collect_processes.sh
│       └── collect_metrics.sh
│
├── docker/
│   ├── docker-compose.yml           # Backend + PostgreSQL with healthcheck
│   └── cronjob.yaml                 # Kubernetes CronJob for metric fetcher
│
├── database/
│   └── init.sql                     # anomaly_results table schema
│
├── docs/
│   ├── architecture.md
│   ├── command_log.md               # Full command history by phase
│   ├── prometheus_queries.md
│   └── report-notes.md              # ML findings and thesis write-up
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml                # Lint → Build → Test pipeline
│
├── setup.sh                         # Installs all Python dependencies
├── start.sh                         # Starts port-forwards + backend
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

### 1. Install Python dependencies
```bash
bash setup.sh
```

### 2. Prepare dataset and train model
```bash
python ml/prepare_dataset.py
python ml/train_model.py
```

### 3. Start all services
```bash
# Stop any running Docker Compose containers first
docker compose -f docker/docker-compose.yml down

# Start port-forwards and backend
bash start.sh
```

This starts:
- Prometheus → http://localhost:9090
- Grafana → http://localhost:3000
- PostgreSQL → localhost:5432
- Backend API → http://localhost:8000

### 4. Start anomaly detector
```bash
python ml/anomaly_detector.py
```

The detector polls Prometheus every 30 seconds, runs each reading through the model, and stores results in PostgreSQL.

### 5. Query results

```bash
# All recent results
curl http://localhost:8000/anomalies

# Only flagged anomalies
curl "http://localhost:8000/anomalies?only_anomalies=true"

# Test predict endpoint manually
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_percent": 2.344, "timestamp": "2014-02-26T22:05:00"}'
```

---

## System Architecture

```
Prometheus (live cluster metrics)
        ↓
ml/anomaly_detector.py  (polls every 30s)
        ↓
FastAPI /predict  (Isolation Forest with rolling window)
        ↓
PostgreSQL anomaly_results table
        ↓
GET /anomalies  (REST API query)
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root |
| GET | `/health` | Service status |
| GET | `/metrics/history` | Recent cluster metrics from database |
| POST | `/predict` | Run anomaly detection on a CPU reading |
| GET | `/anomalies` | Query stored anomaly detection results |

### POST /predict
```json
// Request
{ "cpu_percent": 2.344, "timestamp": "2014-02-26T22:05:00" }

// Response
{ "timestamp": "2014-02-26T22:05:00", "cpu_percent": 2.344, "anomaly": true, "message": "ANOMALY DETECTED" }
```

### GET /anomalies
```bash
# All results (default 50)
curl http://localhost:8000/anomalies

# Only anomalies
curl "http://localhost:8000/anomalies?only_anomalies=true"

# Custom limit
curl "http://localhost:8000/anomalies?limit=100"
```

---

## AI Anomaly Detection — Results

**Dataset:** NAB `ec2_cpu_utilization_24ae8d.csv`  
**Ground truth:** 2 anomalies manually verified by Numenta researchers  
**Rows:** 4,032 at 5-minute intervals

| Model | Flagged | Caught | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Isolation Forest | 4 | 1/2 | 0.25 | 0.50 | 0.33 |
| Local Outlier Factor | 4 | 1/2 | 0.25 | 0.50 | 0.33 |

Both models correctly detected the point anomaly at `2014-02-26 22:05:00` (CPU spike to 2.344%, ~17x above baseline). The contextual anomaly at `2014-02-27 17:15:00` was missed by both, consistent with known limitations of unsupervised density-based methods on contextual anomalies.

Isolation Forest selected for API integration due to lower computational complexity and support for online inference. The `/predict` endpoint uses a 12-point rolling window to replicate the statistical context used during training.

See `docs/report-notes.md` for full findings and thesis write-up.

---

## CI/CD Pipeline

Every push to `main` triggers:

1. **Lint Python** — flake8 on `Backend/app/` and `ml/`
2. **Build Docker Image** — builds backend via docker compose
3. **Test Predict Endpoint** — trains model, starts backend, primes rolling window, asserts `normal=false` and `spike=true`

---

## Thesis Phases

- [x] Phase 1 — Research
- [x] Phase 2 — Architecture Design
- [x] Phase 3 — Kubernetes + Prometheus + Grafana Setup
- [x] Phase 4 — AI Anomaly Detection (Isolation Forest on NAB dataset)
- [x] Phase 5 — Platform Engineering Layer (live detector + /anomalies endpoint)
- [ ] Phase 6 — Evaluation (alert count before vs after AI)

---

## Key Design Decisions

**Why Kubernetes over a custom backend?**
Kubernetes is the industry standard for container orchestration. Building the monitoring system natively in Kubernetes means the architecture reflects real-world DevOps practice.

**Why Prometheus over custom bash collection?**
Prometheus natively scrapes cluster metrics with higher reliability and lower overhead than custom shell scripts. Shell-based collectors were prototyped early and archived in `scripts/legacy/`.

**Why Isolation Forest for anomaly detection?**
Isolation Forest is unsupervised and requires no labelled training data from your own system, making it practical for a project of this scope and timeline.

**Why compare with Local Outlier Factor?**
LOF was evaluated as a theoretically stronger candidate for contextual anomalies. Both models produced identical results, strengthening the conclusion that the missed anomaly represents a genuine algorithmic limitation rather than a model selection issue.

**Why a rolling window in the predict endpoint?**
Single-point inference without context produces poor results. A 12-point in-memory deque replicates the statistical context the model was trained on, enabling accurate real-time inference.

**Why store results in PostgreSQL?**
Persisting predictions enables historical querying, trend analysis, and the before/after evaluation needed for the thesis. In-memory state would be lost on every restart.

---


- A case study: *"Reducing Alert Fatigue Using AI in DevOps"*
