from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd


DEFAULT_RULE_COLS = [
    "event_count",
    "motion_count_total",
    "night_motion_count",
    "morning_motion_count",
    "day_motion_count",
    "evening_motion_count",
    "longest_inactivity_gap_minutes",
    "active_sensors_count",
]

def fit_rule_thresholds(train_df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, float]:
    rules = config.get("rule_model", {})
    upper_p = rules.get("upper_percentile", 95)
    lower_p = rules.get("lower_percentile", 5)

    thresholds = {}
    for col in DEFAULT_RULE_COLS:
        if col in train_df.columns:
            thresholds[f"{col}_low"] = float(np.nanpercentile(train_df[col], lower_p))
            thresholds[f"{col}_high"] = float(np.nanpercentile(train_df[col], upper_p))

    thresholds["severe_inactivity_minutes"] = float(rules.get("severe_inactivity_minutes", 720))
    return thresholds


def predict_rules(df: pd.DataFrame, thresholds: Dict[str, float]) -> pd.DataFrame:
    results = []

    for _, row in df.iterrows():
        reasons = []
        severity_points = 0

        if "longest_inactivity_gap_minutes" in row:
            if row["longest_inactivity_gap_minutes"] > thresholds.get("longest_inactivity_gap_minutes_high", 99999):
                reasons.append("inactivity")
                severity_points += 2
            if row["longest_inactivity_gap_minutes"] > thresholds.get("severe_inactivity_minutes", 720):
                reasons.append("severe_inactivity")
                severity_points += 3

        if "night_motion_count" in row and row["night_motion_count"] > thresholds.get("night_motion_count_high", 99999):
            reasons.append("unusual_night_movement")
            severity_points += 1

        if "day_motion_count" in row and row["day_motion_count"] < thresholds.get("day_motion_count_low", -1):
            reasons.append("missed_daytime_activity")
            severity_points += 1

        if "evening_motion_count" in row and row["evening_motion_count"] < thresholds.get("evening_motion_count_low", -1):
            reasons.append("missed_evening_activity")
            severity_points += 1

        if "morning_motion_count" in row and row["morning_motion_count"] < thresholds.get("morning_motion_count_low", -1):
            reasons.append("missed_morning_routine")
            severity_points += 1

        if "event_count" in row and row["event_count"] < thresholds.get("event_count_low", -1):
            reasons.append("possible_sensor_failure_or_missing_data")
            severity_points += 2

        if "active_sensors_count" in row and row["active_sensors_count"] < thresholds.get("active_sensors_count_low", -1):
            reasons.append("possible_sensor_failure_or_missing_data")
            severity_points += 1


        is_anomaly = int(len(reasons) > 0)
        anomaly_type = ";".join(sorted(set(reasons))) if reasons else "normal"
        score = min(1.0, severity_points / 5.0)

        results.append(
            {
                "date": row["date"],
                "rule_is_anomaly": is_anomaly,
                "rule_anomaly_score": score,
                "rule_anomaly_type": anomaly_type,
            }
        )

    return pd.DataFrame(results)
