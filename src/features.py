from __future__ import annotations

from typing import Dict, List, Any
import numpy as np
import pandas as pd

from src.load_data import infer_sensor_type


def _is_motion_event(df: pd.DataFrame) -> pd.Series:
    """Detect usable activity events across both classic CASAS IDs and room-name CSVs.

    Classic CASAS often uses M001/M002 motion sensors.
    The Aruba CSV used here may already contain room names such as Bedroom/Bathroom.
    Therefore, any ON/OPEN/TRUE/1 event from a non-temperature/non-light sensor is treated
    as an ambient activity event.
    """
    msg = df["message"].astype(str).str.upper().str.strip()
    sensor_type = df.get("sensor_type", pd.Series("other", index=df.index)).astype(str).str.lower()
    active_message = msg.isin(["ON", "OPEN", "1", "TRUE", "PRESENT", "ACTIVE"])
    ignored_type = sensor_type.isin(["temperature", "light"])
    return active_message & ~ignored_type


def add_sensor_metadata(events: pd.DataFrame, sensor_groups: Dict[str, List[str]] | None = None) -> pd.DataFrame:
    events = events.copy()
    events["sensor_type"] = events["sensor_id"].apply(infer_sensor_type)
    events["room"] = "unknown"

    sensor_groups = sensor_groups or {}
    reverse = {}
    for room, sensors in sensor_groups.items():
        for sensor in sensors:
            reverse[str(sensor)] = room

    if reverse:
        events["room"] = events["sensor_id"].map(reverse).fillna("unknown")
    return events


def longest_gap_minutes(timestamps: pd.Series) -> float:
    if timestamps.empty:
        return 1440.0
    ts = pd.to_datetime(timestamps).sort_values()
    # Include day boundaries to catch inactivity before first and after last motion.
    day_start = ts.iloc[0].normalize()
    day_end = day_start + pd.Timedelta(days=1)
    all_points = pd.concat([pd.Series([day_start]), ts, pd.Series([day_end])]).sort_values()
    gaps = all_points.diff().dt.total_seconds().dropna() / 60.0
    return float(gaps.max()) if not gaps.empty else 1440.0


def extract_daily_features(events: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Convert event stream into daily routine features."""
    sensor_groups = config.get("sensor_groups", {})
    tw = config.get("time_windows", {})
    events = add_sensor_metadata(events, sensor_groups=sensor_groups)
    motion_mask = _is_motion_event(events)
    motion_events = events[motion_mask].copy()

    daily_rows = []
    all_dates = sorted(events["date"].unique())

    for date in all_dates:
        day_events = events[events["date"] == date]
        day_motion = motion_events[motion_events["date"] == date]

        night = day_motion[(day_motion["hour"] >= tw.get("night_start_hour", 0)) & (day_motion["hour"] <= tw.get("night_end_hour", 5))]
        morning = day_motion[(day_motion["hour"] >= tw.get("morning_start_hour", 6)) & (day_motion["hour"] <= tw.get("morning_end_hour", 11))]
        daytime = day_motion[(day_motion["hour"] >= tw.get("day_start_hour", 12)) & (day_motion["hour"] <= tw.get("day_end_hour", 17))]
        evening = day_motion[(day_motion["hour"] >= tw.get("evening_start_hour", 18)) & (day_motion["hour"] <= tw.get("evening_end_hour", 23))]

        first_motion = float(day_motion["minute_of_day"].min()) if not day_motion.empty else np.nan
        last_motion = float(day_motion["minute_of_day"].max()) if not day_motion.empty else np.nan

        row = {
            "date": date,
            "event_count": int(len(day_events)),
            "motion_count_total": int(len(day_motion)),
            "door_event_count": int((day_events["sensor_type"] == "door").sum()),
            "night_motion_count": int(len(night)),
            "morning_motion_count": int(len(morning)),
            "day_motion_count": int(len(daytime)),
            "evening_motion_count": int(len(evening)),
            "first_motion_minute": first_motion,
            "last_motion_minute": last_motion,
            "longest_inactivity_gap_minutes": longest_gap_minutes(day_motion["timestamp"]),
            "active_sensors_count": int(day_events["sensor_id"].nunique()),
            "active_sensor_types_count": int(day_events["sensor_type"].nunique()),
        }

        for room in sorted(set(day_events["room"].unique()) - {"unknown"}):
            row[f"{room}_motion_count"] = int(((day_motion["room"] == room)).sum())

        daily_rows.append(row)

    features = pd.DataFrame(daily_rows)
    features = features.sort_values("date").reset_index(drop=True)
    numeric_cols = features.select_dtypes(include=[np.number]).columns
    features[numeric_cols] = features[numeric_cols].fillna(features[numeric_cols].median(numeric_only=True)).fillna(0)
    return features


def extract_hourly_features(events: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Daily features built from hourly aggregated counts. Useful for privacy level P2."""
    events = add_sensor_metadata(events, sensor_groups=config.get("sensor_groups", {}))
    grouped = (
        events.groupby(["date", "hour", "sensor_type"])
        .size()
        .reset_index(name="count")
    )
    pivot = grouped.pivot_table(index="date", columns=["sensor_type", "hour"], values="count", fill_value=0)
    pivot.columns = [f"{sensor_type}_h{hour:02d}" for sensor_type, hour in pivot.columns]
    pivot = pivot.reset_index()
    return pivot


def numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "date" and pd.api.types.is_numeric_dtype(df[c])]
