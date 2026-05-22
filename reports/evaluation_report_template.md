# Evaluation Report Template

## 1. Experimental setup

Dataset used:

Number of days:

Number of events:

Sensor types:

Privacy levels tested:

Models tested:

- rule-based baseline
- Isolation Forest

## 2. Scenarios

| Scenario | Description | Expected result |
|---|---|---|
| Normal routine | Typical days without injected anomaly | Low anomaly score |
| Inactivity | Reduced movement during active period | Inactivity anomaly |
| Night movement | Increased movement during 00:00-05:00 | Night movement anomaly |
| Missed routine | Expected morning activity missing | Missed routine anomaly |
| Sensor failure | Missing/insufficient sensor data | Sensor failure warning |

## 3. Metrics

| Metric | Rule-based | Isolation Forest |
|---|---:|---:|
| Accuracy |  |  |
| Precision |  |  |
| Recall |  |  |
| F1-score |  |  |
| False positive rate |  |  |

## 4. Privacy/utility trade-off

| Privacy level | Data retained | Detection quality | Privacy risk |
|---|---|---:|---:|
| P0 Raw-derived | daily features from exact events |  |  |
| P1 Pseudonymized | anonymous sensor IDs |  |  |
| P2 Hourly aggregated | hourly counts |  |  |
| P3 Daily minimized | daily summary only |  |  |

## 5. False-positive analysis

Discuss days incorrectly flagged as anomalous.

Possible causes:

- irregular but harmless routine
- sparse sensor data
- missing events
- threshold too strict
- model trained on too little data

## 6. Failure-case analysis

Describe how the system behaves when sensor data is missing or unreliable.

The correct behavior is to report possible sensor failure or insufficient data, not to infer a resident emergency.

## 7. Limitations

- not clinically validated
- depends on stable routine
- public dataset may not represent all residents
- synthetic anomalies may simplify real-world behavior
- no actual deployment validation
