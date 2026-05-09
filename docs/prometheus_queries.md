# Prometheus Queries Reference

Queries used throughout the project for monitoring cluster health.
These form the basis of the metrics the AI anomaly detection model will analyse.

---

## CPU Usage per Node
```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
Returns CPU usage percentage per node. Idle time subtracted from 100 gives active usage.

---

## Memory Usage per Node
```promql
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```
Returns memory usage as a percentage of total available memory per node.

---

## Pod Count per Node
```promql
count by (node) (kube_pod_info)
```
Returns how many pods are scheduled on each node in the cluster.

---

## Notes
- All queries are run against the Prometheus datasource in Grafana Explore
- Time range set to Last 1 hour during Day 3 exploration
- Cluster nodes: `desktop-control-plane`, `desktop-worker`, `desktop-worker2`