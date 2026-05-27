# Privacy-Aware Smart Home Monitoring for Daily Routine Anomaly Detection

**Author:** Andrei Bălan  
**Affiliation:** Faculty of Industrial Engineering and Robotics

## Abstract

This paper presents a privacy-aware smart-home monitoring prototype for detecting daily routine anomalies using ambient sensor data. The system models routine behavior from minimized sensor-derived features and detects deviations such as inactivity, unusual nighttime movement, missed routines and possible sensor failure. The prototype compares rule-based anomaly detection and Isolation Forest under different privacy representations, including raw-derived features, sensor pseudonymization, hourly aggregation and daily minimized features. The system includes a caregiver notification policy and dashboard while avoiding camera, audio and biometric data. Results are reported as a course prototype and are not presented as clinically validated evidence.

## I. Introduction

Smart homes can support independent living by monitoring routine behavior through ambient sensors. However, continuous monitoring can become intrusive if raw data is collected unnecessarily. This project addresses the trade-off between anomaly detection quality and privacy preservation.

## II. Project Specification

The objective is to build an isolated prototype that uses public or simulated smart-home data to detect daily routine anomalies. The input consists of timestamped ambient sensor events. The output consists of anomaly scores, anomaly labels, notification levels and dashboard visualizations.

## III. Dataset Protocol

The recommended dataset is CASAS Aruba or an equivalent public ambient smart-home dataset. The raw events are parsed, normalized and transformed into daily and hourly feature vectors. Synthetic anomaly scenarios may be used when labeled anomalies are unavailable.

## IV. System Architecture

The architecture contains five stages: data ingestion, feature extraction, privacy transformation, anomaly detection and dashboard presentation. The system avoids cameras, microphones and biometric data.

## V. Anomaly Detection Method

Two anomaly detection methods are implemented. The first is a rule-based baseline using thresholds for inactivity, nighttime movement, missed routines and missing data. The second is an Isolation Forest model trained on routine feature vectors.

## VI. Privacy-by-Design

Privacy is addressed through data minimization, sensor pseudonymization and aggregation. Four privacy levels are compared: raw-derived features, pseudonymized sensors, hourly aggregation and daily minimized features.

## VII. Evaluation

The evaluation considers normal routine, inactivity, unusual nighttime movement, missed routine and sensor failure scenarios. Metrics include precision, recall, F1-score, false-positive rate and qualitative privacy risk.

## VIII. Ethical and Safety Review

The system is intended only as a course prototype. It does not perform medical diagnosis, does not confirm falls and does not replace emergency care. Notifications are worded as routine deviations rather than health conclusions.

## IX. Conclusion

The prototype demonstrates that daily routine anomalies can be detected from ambient smart-home data while reducing sensitive data collection through aggregation and minimization. The results should be interpreted within the limited scope of a short academic project.
