# Project 35 - Privacy-Aware Smart Home Monitoring for Daily Routine Anomaly Detection

Prototype for ambient assisted living routine monitoring using public or simulated smart-home sensor data.

The project detects daily routine anomalies while minimizing sensitive data collection. It includes:

- dataset protocol
- preprocessing pipeline
- privacy transformations
- rule-based anomaly baseline
- Isolation Forest anomaly detector
- false-positive and failure-case analysis
- caregiver notification policy
- Streamlit dashboard
- IEEE-style paper template

> Important: this is a course prototype, not a medical or clinically validated monitoring system.

---

## 1. Recommended dataset

Use a public smart-home ambient sensor dataset, preferably CASAS Aruba.

Expected raw format examples:

```txt
2010-11-04 00:03:50.209589 M003 ON Sleeping
2010-11-04 00:03:57.399391 M003 OFF Sleeping
2010-11-04 00:15:08.984841 D001 OPEN Sleeping
```

or CSV:

```csv
date,time,sensor_id,message,activity
2010-11-04,00:03:50,M003,ON,Sleeping
```

Place your dataset here:

```txt
data/raw/
```

Recommended filename:

```txt
data/raw/casas_aruba.txt
```

---

## 2. Quick start with demo data

This project includes a synthetic demo generator so the code runs before you add the real dataset.

```bash
pip install -r requirements.txt
python scripts/03_generate_demo_data.py
python scripts/01_prepare_dataset.py --input data/raw/aruba_fixed.csv
python scripts/02_train_evaluate.py
streamlit run dashboard/app.py
```

---

## 3. Run with your CASAS dataset

After placing the dataset in `data/raw/`, run:

```bash
python scripts/01_prepare_dataset.py --input data/raw/casas_aruba.txt
python scripts/02_train_evaluate.py
streamlit run dashboard/app.py
```

If your dataset already has a label file, put it as:

```txt
data/processed/labels.csv
```

Expected label file:

```csv
date,y_true,anomaly_type
2010-11-20,0,normal
2010-11-21,1,inactivity
```

If no labels exist, the project still produces anomaly scores, but precision/recall/F1 cannot be computed.

---

## 4. Project architecture

```txt
CASAS / public dataset
        ↓
load_data.py
        ↓
features.py
        ↓
privacy.py
        ↓
anomaly_rules.py + anomaly_iforest.py
        ↓
evaluation.py
        ↓
Streamlit dashboard
```

---

## 5. Privacy levels

The project compares detection under four privacy settings:

| Level | Description | Privacy | Utility |
|---|---|---:|---:|
| P0 Raw-derived | Exact timestamp/sensor events converted to daily features | Low | High |
| P1 Pseudonymized | Sensor IDs replaced by anonymous IDs | Medium | High |
| P2 Hourly aggregated | Counts by hour and sensor type | High | Medium-High |
| P3 Daily minimized | Only daily summary features | Very High | Medium |

This replaces network anonymity comparisons such as Tor/VPN, which are not relevant to this project title.

---

## 6. Main anomaly types

- inactivity anomaly
- unusual nighttime movement
- missed morning routine
- possible sensor failure / insufficient data

The prototype never claims clinical detection of falls, illness, or emergency conditions.

---

## 7. Deliverables covered

- Prototype: Python pipeline + Streamlit dashboard
- Dataset protocol: `reports/dataset_protocol.md`
- Dashboard: `dashboard/app.py`
- Evaluation report: `reports/evaluation_report_template.md`
- IEEE-style paper: `reports/ieee_paper_template.md`
- Integrated specification: `docs/project_specification.md`

---

## 8. Suggested presentation claim

This project implements a privacy-aware smart-home monitoring prototype for detecting routine anomalies from ambient sensor data. It compares raw-derived, pseudonymized, aggregated and minimized data representations, and evaluates the trade-off between privacy and anomaly detection quality.
