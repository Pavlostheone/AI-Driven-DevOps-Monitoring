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
| Dataset | NAB (Numenta Anomaly Benchmark) |
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
│       ├── services/
│       ├── db/
│       ├── schemas/
│       └── utils/
│
├── scripts/
│   ├── collect_pod_metrics.sh
│   ├── collect_docker.sh
│   ├── healthcheck.sh
│   ├── config.env
│   ├── common.sh
│   ├── utils.sh
│   └── legacy/               # Replaced by Prometheus native collection
│       ├── collect_cpu.sh
│       ├── collect_memory.sh
│       ├── collect_disk.sh
│       ├── collect_network.sh
│       ├── collect_processes.sh
│       └── collect_metrics.sh
│
├── ml/
│   ├── train_model.py
│   └── model.pkl
│
├── docs/
│   ├── architecture.md
│   └── command_log.md
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
└── README.md
```

---

## Getting Started

### Prerequisites
- Docker Desktop with Kubernetes enabled
- Helm v3+
- kubectl
- Git Bash (Windows)

### 1. Verify cluster is running
```bash
kubectl get nodes
```

### 2. Deploy Prometheus + Grafana
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 3. Access Grafana
```bash
# Get admin password
kubectl --namespace monitoring get secrets monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d ; echo

# Forward to localhost
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```
Open `http://localhost:3000` — login with `admin` and the password above.

### 4. Access Prometheus
```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-st-prometheus 9090:9090
```
Open `http://localhost:9090`

---

## Thesis Phases

- [x] Phase 1 — Research
- [x] Phase 2 — Architecture Design
- [x] Phase 3 — Kubernetes + Prometheus + Grafana Setup
- [ ] Phase 4 — AI Anomaly Detection (Isolation Forest on NAB dataset)
- [ ] Phase 5 — Platform Engineering Layer
- [ ] Phase 6 — Evaluation (alert count before vs after AI)

---

## Key Design Decisions

**Why Kubernetes over a custom backend?**  
Kubernetes is the industry standard for container orchestration. Building the monitoring system natively in Kubernetes means the architecture reflects real-world DevOps practice rather than a simplified standalone backend.

**Why Prometheus over custom bash collection?**  
Prometheus natively scrapes cluster metrics with higher reliability, lower overhead, and better data quality than custom shell scripts. Shell-based collectors were prototyped early in the project and archived in `scripts/legacy/` once Prometheus was deployed.

**Why Isolation Forest for anomaly detection?**  
Isolation Forest is an unsupervised algorithm well suited to anomaly detection on time-series metric data. It does not require labeled training data from your own system, making it practical for a project of this scope and timeline.

---

## Portfolio Value

This project is presentable as:
- A working GitHub repository with real Kubernetes infrastructure
- A live or recorded demo
- A case study: *"Reducing Alert Fatigue Using AI in DevOps"*
