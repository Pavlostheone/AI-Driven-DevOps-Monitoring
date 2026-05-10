# ML Model Evaluation — Findings & Write-Up
**Project:** AI-Driven DevOps Monitoring System  
**Dataset:** NAB — `ec2_cpu_utilization_24ae8d.csv`  
**Date:** May 2026

---

## Dataset

| Property | Value |
|---|---|
| Source | Numenta Anomaly Benchmark (NAB) |
| Total rows | 4,032 |
| Time range | ~2 weeks of 5-minute interval EC2 CPU readings |
| Labeled anomalies | 2 (manually verified by Numenta researchers) |
| Normal rows | 4,030 |

**Ground truth anomaly timestamps:**
- `2014-02-26 22:05:00` — CPU spike to **2.344%** (17x above baseline of ~0.132%)
- `2014-02-27 17:15:00` — CPU reading of **0.602%** (contextual anomaly)

---

## Feature Engineering

Raw CPU percentage alone is insufficient for anomaly detection. The following features were derived to give models temporal and statistical context:

| Feature | Description |
|---|---|
| `cpu_percent` | Raw CPU reading |
| `rolling_mean` | 12-point rolling average (~1 hour window) |
| `rolling_std` | 12-point rolling standard deviation |
| `rolling_max` | 12-point rolling maximum |
| `diff` | Point-to-point change in CPU |
| `hour` | Hour of day (captures daily usage patterns) |
| `day_of_week` | Day of week (captures weekly patterns) |

---

## Models Evaluated

### Model 1 — Isolation Forest
An ensemble method that isolates anomalies by randomly partitioning the feature space. Points that require fewer partitions to isolate are scored as anomalies. Well-suited for **point anomalies** — sudden, large deviations from baseline.

**Configuration:**
- `n_estimators`: 100
- `contamination`: 0.001
- `random_state`: 42

### Model 2 — Local Outlier Factor (LOF)
A density-based method that scores each point relative to its local neighbourhood. Points in regions of significantly lower density than their neighbours are flagged as anomalies. Theoretically better suited for **contextual anomalies** than Isolation Forest.

**Configuration:**
- `n_neighbors`: 20
- `contamination`: 0.001

---

## Results

| Model | Total Flagged | Ground Truth Caught | Precision | Recall | F1 Score |
|---|---|---|---|---|---|
| Isolation Forest | 4 | 1 / 2 | 0.25 | 0.50 | 0.33 |
| Local Outlier Factor | 4 | 1 / 2 | 0.25 | 0.50 | 0.33 |

**Ground truth breakdown:**

| Timestamp | CPU % | Isolation Forest | LOF |
|---|---|---|---|
| 2014-02-26 22:05:00 | 2.344 | ✅ Detected | ✅ Detected |
| 2014-02-27 17:15:00 | 0.602 | ❌ Missed | ❌ Missed |

---

## Analysis

### What the models got right
Both models independently and correctly identified the anomaly at `22:05:00`. With a CPU value 17x above the surrounding baseline, this is a classic **point anomaly** — the type both algorithms are designed to detect. The fact that two different algorithmic approaches agree on this detection increases confidence in the result.

### What the models missed
The anomaly at `17:15:00` (0.602%) was missed by both models. This reading is only ~4.5x above baseline, and crucially, its anomalous nature is not determined by its absolute value alone — it is anomalous *in context* of the surrounding time series pattern. This is a **contextual anomaly**, a category that requires understanding temporal sequences rather than point-in-time feature distributions.

### False positives
Both models flagged 4 points total, of which 1 was a verified ground truth anomaly, producing 3 false positives. These false positives represent genuine statistical outliers that both algorithms correctly identified as unusual — however, Numenta's researchers did not classify them as operationally significant anomalies. This reflects a real-world precision/recall tradeoff: a more sensitive model catches more true anomalies but also raises more false alarms.

---

## Thesis Write-Up

### Model Selection and Evaluation

Two unsupervised anomaly detection models were evaluated against the Numenta Anomaly Benchmark (NAB) dataset for EC2 CPU utilisation, which provides 4,032 labelled data points with two manually verified anomalies identified by Numenta researchers.

Isolation Forest and Local Outlier Factor were selected as representative unsupervised approaches appropriate for infrastructure monitoring, where labelled training data is rarely available in production environments. Both models were trained on engineered features incorporating rolling statistics and temporal context to improve sensitivity to usage pattern deviations.

Both models achieved identical performance: precision of 0.25, recall of 0.50, and F1 score of 0.33. The point anomaly at `2014-02-26 22:05:00`, characterised by a CPU spike to 2.344% — approximately 17 times the surrounding baseline — was correctly detected by both models. The contextual anomaly at `2014-02-27 17:15:00` (0.602%) was missed by both, consistent with established literature demonstrating that density-based and ensemble isolation methods underperform on contextual anomalies that require temporal sequence modelling rather than static feature distribution analysis (Chandola et al., 2009).

The agreement between two algorithmically distinct models on both detections and misses strengthens confidence in these findings. Isolation Forest was selected for API integration based on its lower computational complexity and suitability for real-time inference, as LOF requires the full dataset at prediction time and does not naturally support online learning.

A key limitation identified is that neither model is capable of detecting subtle contextual anomalies without sequence-aware architecture. Future work should evaluate LSTM autoencoders or Prophet-based anomaly detection, which model temporal dependencies explicitly and have demonstrated stronger recall on contextual anomalies in time series benchmarks.

---

## Citation to Include

> Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys*, 41(3), 1–58. https://doi.org/10.1145/1541880.1541882

> Lavin, A., & Ahmad, S. (2015). Evaluating Real-Time Anomaly Detection Algorithms — The Numenta Anomaly Benchmark. *14th IEEE International Conference on Machine Learning and Applications*. https://doi.org/10.1109/ICMLA.2015.141

---

