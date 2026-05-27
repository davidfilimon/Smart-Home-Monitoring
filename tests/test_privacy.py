import pandas as pd
import pytest
from src.privacy import pseudonymize_sensors, make_privacy_feature_sets

CONFIG = {
    "time_windows": {
        "night_start_hour": 0, "night_end_hour": 5,
        "morning_start_hour": 6, "morning_end_hour": 11,
        "day_start_hour": 12, "day_end_hour": 17,
        "evening_start_hour": 18, "evening_end_hour": 23,
    },
    "sensor_groups": {}
}

def make_events():
    return pd.DataFrame([
        {"sensor_id": "M001", "date": "2011-01-01", "hour": 8,
         "minute_of_day": 480, "message": "ON", "activity": "",
         "timestamp": pd.Timestamp("2011-01-01 08:00:00")},
        {"sensor_id": "D002", "date": "2011-01-01", "hour": 9,
         "minute_of_day": 540, "message": "OPEN", "activity": "",
         "timestamp": pd.Timestamp("2011-01-01 09:00:00")},
        {"sensor_id": "M001", "date": "2011-01-01", "hour": 20,
         "minute_of_day": 1200, "message": "ON", "activity": "",
         "timestamp": pd.Timestamp("2011-01-01 20:00:00")},
        {"sensor_id": "M003", "date": "2011-01-02", "hour": 7,
         "minute_of_day": 420, "message": "ON", "activity": "",
         "timestamp": pd.Timestamp("2011-01-02 07:00:00")},
        {"sensor_id": "D002", "date": "2011-01-02", "hour": 14,
         "minute_of_day": 840, "message": "OPEN", "activity": "",
         "timestamp": pd.Timestamp("2011-01-02 14:00:00")},
    ])


def test_pseudonymize_inlocuieste_id_urile():
    df = make_events()
    result = pseudonymize_sensors(df)
    assert "M001" not in result["sensor_id"].values
    assert "D002" not in result["sensor_id"].values
    assert "M003" not in result["sensor_id"].values


def test_pseudonymize_genereaza_format_corect():
    df = make_events()
    result = pseudonymize_sensors(df)
    for sid in result["sensor_id"].unique():
        assert sid.startswith("S")
        assert len(sid) == 4


def test_pseudonymize_pastreaza_id_original():
    df = make_events()
    result = pseudonymize_sensors(df)
    assert "sensor_id_original" in result.columns
    assert "M001" in result["sensor_id_original"].values


def test_pseudonymize_stabil_acelasi_senzor():
    df = make_events()
    result = pseudonymize_sensors(df)
    m001_rows = result[result["sensor_id_original"] == "M001"]
    assert m001_rows["sensor_id"].nunique() == 1


def test_make_privacy_returneaza_toate_nivelurile():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    assert "P0_raw_derived" in result
    assert "P1_pseudonymized" in result
    assert "P2_hourly_aggregated" in result
    assert "P3_daily_minimized" in result
    assert "P4_boolean_flags" in result


def test_p0_are_mai_multe_coloane_decat_p3():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    assert len(result["P0_raw_derived"].columns) > len(result["P3_daily_minimized"].columns)


def test_p1_nu_contine_id_uri_originale():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    p1 = result["P1_pseudonymized"]
    assert "M001" not in str(p1.values)
    assert "D002" not in str(p1.values)


def test_p3_contine_doar_coloanele_minimizate():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    p3 = result["P3_daily_minimized"]
    expected_cols = {"date", "motion_count_total", "night_motion_count",
                     "morning_motion_count", "longest_inactivity_gap_minutes",
                     "first_motion_minute", "last_motion_minute",
                     "active_sensor_types_count"}
    assert set(p3.columns) == expected_cols


def test_p4_contine_doar_flaguri_booleane():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    p4 = result["P4_boolean_flags"]
    bool_cols = [c for c in p4.columns if c != "date"]
    for col in bool_cols:
        assert p4[col].dtype == bool, f"Coloana {col} nu e boolean"


def test_p4_valori_corecte():
    df = make_events()
    result = make_privacy_feature_sets(df, CONFIG)
    p4 = result["P4_boolean_flags"]
    row = p4[p4["date"] == "2011-01-01"].iloc[0]
    assert row["was_active_morning"] == True
    assert row["was_active_evening"] == True