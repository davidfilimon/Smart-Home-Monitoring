import pandas as pd
import numpy as np
import pytest
from src.anomaly_rules import predict_rules, fit_rule_thresholds, DEFAULT_RULE_COLS

THRESHOLDS = {
    "longest_inactivity_gap_minutes_high": 300.0,
    "longest_inactivity_gap_minutes_low": 10.0,
    "severe_inactivity_minutes": 720.0,
    "night_motion_count_high": 10.0,
    "night_motion_count_low": 0.0,
    "morning_motion_count_high": 30.0,
    "morning_motion_count_low": 3.0,
    "day_motion_count_high": 40.0,
    "day_motion_count_low": 3.0,
    "evening_motion_count_high": 30.0,
    "evening_motion_count_low": 3.0,
    "event_count_high": 200.0,
    "event_count_low": 20.0,
    "motion_count_total_high": 100.0,
    "motion_count_total_low": 5.0,
    "active_sensors_count_high": 20.0,
    "active_sensors_count_low": 2.0,
}

def make_normal_row(date="2011-01-01"):
    return {
        "date": date,
        "longest_inactivity_gap_minutes": 60.0,
        "night_motion_count": 2,
        "morning_motion_count": 10,
        "day_motion_count": 15,
        "evening_motion_count": 8,
        "event_count": 100,
        "motion_count_total": 50,
        "active_sensors_count": 5,
    }


def test_zi_normala():
    df = pd.DataFrame([make_normal_row()])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 0
    assert result.iloc[0]["rule_anomaly_type"] == "normal"
    assert result.iloc[0]["rule_anomaly_score"] == 0.0


def test_inactivitate_severa():
    row = make_normal_row()
    row["longest_inactivity_gap_minutes"] = 800.0
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "severe_inactivity" in result.iloc[0]["rule_anomaly_type"]


def test_miscare_neobisnuita_noaptea():
    row = make_normal_row()
    row["night_motion_count"] = 20
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "unusual_night_movement" in result.iloc[0]["rule_anomaly_type"]


def test_lipsa_rutina_dimineata():
    row = make_normal_row()
    row["morning_motion_count"] = 1
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "missed_morning_routine" in result.iloc[0]["rule_anomaly_type"]


def test_posibil_senzor_defect():
    row = make_normal_row()
    row["event_count"] = 5
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "possible_sensor_failure_or_missing_data" in result.iloc[0]["rule_anomaly_type"]


def test_anomalii_multiple_simultan():
    row = make_normal_row()
    row["longest_inactivity_gap_minutes"] = 800.0
    row["night_motion_count"] = 20
    row["morning_motion_count"] = 1
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert result.iloc[0]["rule_anomaly_score"] > 0.5


def test_lipsa_activitate_zi():
    row = make_normal_row()
    row["day_motion_count"] = 0
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "missed_daytime_activity" in result.iloc[0]["rule_anomaly_type"]


def test_lipsa_activitate_seara():
    row = make_normal_row()
    row["evening_motion_count"] = 0
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_is_anomaly"] == 1
    assert "missed_evening_activity" in result.iloc[0]["rule_anomaly_type"]


def test_scor_maxim_clamped_la_1():
    row = make_normal_row()
    row["longest_inactivity_gap_minutes"] = 1440.0
    row["night_motion_count"] = 50
    row["morning_motion_count"] = 0
    row["event_count"] = 2
    row["active_sensors_count"] = 1
    df = pd.DataFrame([row])
    result = predict_rules(df, THRESHOLDS)
    assert result.iloc[0]["rule_anomaly_score"] <= 1.0


def test_fit_rule_thresholds_calculeaza_correct():
    train_df = pd.DataFrame([make_normal_row(f"2011-01-{i:02d}") for i in range(1, 21)])
    config = {
        "rule_model": {
            "upper_percentile": 95,
            "lower_percentile": 5,
            "severe_inactivity_minutes": 720,
        }
    }
    thresholds = fit_rule_thresholds(train_df, config)
    assert "longest_inactivity_gap_minutes_high" in thresholds
    assert "morning_motion_count_low" in thresholds
    assert thresholds["severe_inactivity_minutes"] == 720.0


def test_default_rule_cols_contine_coloanele_noi():
    assert "day_motion_count" in DEFAULT_RULE_COLS
    assert "evening_motion_count" in DEFAULT_RULE_COLS