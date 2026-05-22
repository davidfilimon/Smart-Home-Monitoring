from __future__ import annotations

import pandas as pd


def assign_notification_level(row: pd.Series) -> int:
    """Map anomaly evidence to caregiver notification level.

    Level 0: normal, no notification
    Level 1: dashboard only
    Level 2: soft caregiver notification
    Level 3: urgent check recommendation
    """
    anomaly_text = str(row.get("rule_anomaly_type", "normal"))
    score = max(float(row.get("rule_anomaly_score", 0.0)), float(row.get("iforest_anomaly_score", 0.0)))

    if "severe_inactivity" in anomaly_text:
        return 3
    if "possible_sensor_failure" in anomaly_text:
        return 1
    if "inactivity" in anomaly_text:
        return 2
    if "unusual_night_movement" in anomaly_text or "missed_morning_routine" in anomaly_text:
        return 1 if score < 0.75 else 2
    if int(row.get("iforest_is_anomaly", 0)) == 1:
        return 1 if score < 0.75 else 2
    return 0


def notification_message(level: int, anomaly_type: str) -> str:
    if level == 0:
        return "Normal routine. No notification."
    if level == 1:
        return "Minor routine deviation detected. Dashboard review recommended."
    if level == 2:
        return "Routine anomaly detected. A soft caregiver check is recommended."
    if level == 3:
        return "Severe unusual inactivity detected compared to routine baseline. Urgent check recommended."
    return "Unknown notification level."


def apply_notification_policy(predictions: pd.DataFrame) -> pd.DataFrame:
    out = predictions.copy()
    out["notification_level"] = out.apply(assign_notification_level, axis=1)
    out["notification_message"] = out.apply(
        lambda r: notification_message(int(r["notification_level"]), str(r.get("rule_anomaly_type", ""))),
        axis=1,
    )
    return out
