from __future__ import annotations

from typing import Dict, Any
import pandas as pd

from src.features import extract_daily_features, extract_hourly_features


def pseudonymize_sensors(events: pd.DataFrame) -> pd.DataFrame:
    """Replace real sensor IDs with stable pseudonyms S001, S002, ..."""
    events = events.copy()
    unique_sensors = sorted(events["sensor_id"].astype(str).unique())
    mapping = {sensor: f"S{i+1:03d}" for i, sensor in enumerate(unique_sensors)}
    events["sensor_id_original"] = events["sensor_id"]
    events["sensor_id"] = events["sensor_id"].map(mapping)
    return events


def make_privacy_feature_sets(events: pd.DataFrame, config: Dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Create feature datasets under different privacy levels.

    P0: raw-derived daily features
    P1: pseudonymized raw-derived daily features
    P2: hourly aggregated features
    P3: minimized daily features
    P4: boolean flags for activity patterns
    """
    p0 = extract_daily_features(events, config)

    # Pseudonymization keeps event utility but removes direct sensor identifiers.
    # Since room mapping may depend on original IDs, P1 uses no room map unless the user updates config.
    pseudo_config = dict(config)
    pseudo_config["sensor_groups"] = {}
    p1 = extract_daily_features(pseudonymize_sensors(events), pseudo_config)

    p2 = extract_hourly_features(events, config)

    minimized_cols = [
        "date",
        "motion_count_total",
        "night_motion_count",
        "morning_motion_count",
        "longest_inactivity_gap_minutes",
        "first_motion_minute",
        "last_motion_minute",
        "active_sensor_types_count",
    ]
    minimized_cols = [c for c in minimized_cols if c in p0.columns]
    p3 = p0[minimized_cols].copy()

    p4 = pd.DataFrame({
    "date": p0["date"],
    "was_active_morning": p0["morning_motion_count"] > 0,
    "was_active_night": p0["night_motion_count"] > 0,
    "was_active_day": p0["day_motion_count"] > 0,
    "was_active_evening": p0["evening_motion_count"] > 0,
    "had_long_inactivity": p0["longest_inactivity_gap_minutes"] > 120,})

    return {
    "P0_raw_derived": p0,
    "P1_pseudonymized": p1,
    "P2_hourly_aggregated": p2,
    "P3_daily_minimized": p3,
    "P4_boolean_flags": p4,
    }