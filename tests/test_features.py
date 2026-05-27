import pytest
import pandas as pd
import numpy as np
from src.features import (
    extract_daily_features,
    extract_hourly_features,
    longest_gap_minutes,
    add_sensor_metadata,
    numeric_feature_columns,
)

CONFIG = {
    "time_windows": {
        "night_start_hour": 0, "night_end_hour": 5,
        "morning_start_hour": 6, "morning_end_hour": 11,
        "day_start_hour": 12, "day_end_hour": 17,
        "evening_start_hour": 18, "evening_end_hour": 23,
    },
    "sensor_groups": {}
}

def make_events(rows):
    return pd.DataFrame(rows)

def make_event(date, hour, minute, sensor_id="M001", message="ON"):
    ts = pd.Timestamp(f"{date} {hour:02d}:{minute:02d}:00")
    return {
        "timestamp": ts,
        "date": date,
        "hour": hour,
        "minute_of_day": hour * 60 + minute,
        "sensor_id": sensor_id,
        "message": message,
        "activity": "",
    }


# --- longest_gap_minutes ---

def test_longest_gap_zi_fara_miscare():
    result = longest_gap_minutes(pd.Series([], dtype="datetime64[ns]"))
    assert result == 1440.0

def test_longest_gap_o_singura_miscare():
    ts = pd.Series([pd.Timestamp("2011-01-01 12:00:00")])
    result = longest_gap_minutes(ts)
    assert result == 720.0

def test_longest_gap_doua_miscari_apropiate():
    ts = pd.Series([
        pd.Timestamp("2011-01-01 08:00:00"),
        pd.Timestamp("2011-01-01 08:30:00"),
    ])
    result = longest_gap_minutes(ts)
    # Functia include granitele zilei (00:00 si 24:00)
    # Cel mai mare gap e de la 08:30 pana la sfarsitul zilei = 930 minute
    assert result == 930.0


# --- add_sensor_metadata ---

def test_add_sensor_metadata_tip_corect():
    df = make_events([make_event("2011-01-01", 8, 0, sensor_id="M001")])
    result = add_sensor_metadata(df)
    assert result.iloc[0]["sensor_type"] == "motion"

def test_add_sensor_metadata_usa():
    df = make_events([make_event("2011-01-01", 8, 0, sensor_id="D001")])
    result = add_sensor_metadata(df)
    assert result.iloc[0]["sensor_type"] == "door"

def test_add_sensor_metadata_camera_din_config():
    df = make_events([make_event("2011-01-01", 8, 0, sensor_id="M001")])
    result = add_sensor_metadata(df, sensor_groups={"bedroom": ["M001"]})
    assert result.iloc[0]["room"] == "bedroom"

def test_add_sensor_metadata_camera_necunoscuta():
    df = make_events([make_event("2011-01-01", 8, 0, sensor_id="M001")])
    result = add_sensor_metadata(df, sensor_groups={})
    assert result.iloc[0]["room"] == "unknown"


# --- extract_daily_features ---

def test_extract_daily_features_returneaza_o_linie_per_zi():
    events = make_events([
        make_event("2011-01-01", 8, 0),
        make_event("2011-01-01", 10, 0),
        make_event("2011-01-02", 9, 0),
    ])
    result = extract_daily_features(events, CONFIG)
    assert len(result) == 2

def test_extract_daily_features_contine_coloanele_necesare():
    events = make_events([make_event("2011-01-01", 8, 0)])
    result = extract_daily_features(events, CONFIG)
    for col in ["date", "motion_count_total", "night_motion_count",
                "morning_motion_count", "day_motion_count", "evening_motion_count",
                "longest_inactivity_gap_minutes", "event_count"]:
        assert col in result.columns, f"Coloana lipseste: {col}"

def test_extract_daily_features_numara_corect_miscari_dimineata():
    events = make_events([
        make_event("2011-01-01", 7, 0),
        make_event("2011-01-01", 8, 0),
        make_event("2011-01-01", 20, 0),
    ])
    result = extract_daily_features(events, CONFIG)
    assert result.iloc[0]["morning_motion_count"] == 2
    assert result.iloc[0]["evening_motion_count"] == 1

def test_extract_daily_features_zi_fara_miscare():
    events = make_events([
        make_event("2011-01-01", 8, 0, sensor_id="T001", message="ON"),
    ])
    result = extract_daily_features(events, CONFIG)
    assert result.iloc[0]["motion_count_total"] == 0

def test_extract_daily_features_sortat_dupa_data():
    events = make_events([
        make_event("2011-01-03", 8, 0),
        make_event("2011-01-01", 8, 0),
        make_event("2011-01-02", 8, 0),
    ])
    result = extract_daily_features(events, CONFIG)
    assert list(result["date"]) == ["2011-01-01", "2011-01-02", "2011-01-03"]


# --- extract_hourly_features ---

def test_extract_hourly_features_returneaza_o_linie_per_zi():
    events = make_events([
        make_event("2011-01-01", 8, 0),
        make_event("2011-01-02", 9, 0),
    ])
    result = extract_hourly_features(events, CONFIG)
    assert len(result) == 2

def test_extract_hourly_features_contine_date():
    events = make_events([make_event("2011-01-01", 8, 0)])
    result = extract_hourly_features(events, CONFIG)
    assert "date" in result.columns


# --- numeric_feature_columns ---

def test_numeric_feature_columns_exclude_date():
    df = pd.DataFrame([{"date": "2011-01-01", "motion_count": 5, "score": 0.8}])
    result = numeric_feature_columns(df)
    assert "date" not in result
    assert "motion_count" in result
    assert "score" in result