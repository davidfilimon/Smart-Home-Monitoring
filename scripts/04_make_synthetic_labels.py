from pathlib import Path
import pandas as pd
import numpy as np


def pick_dates(dates, n):
    if len(dates) == 0:
        return []
    idx = np.linspace(0, len(dates) - 1, n).round().astype(int)
    return list(pd.Series(dates).iloc[idx].astype(str))


def main():
    processed_dir = Path("data/processed")
    features_path = processed_dir / "features_daily.csv"

    if not features_path.exists():
        raise FileNotFoundError("Run scripts/01_prepare_dataset.py first.")

    df = pd.read_csv(features_path)
    df["date"] = df["date"].astype(str)

    # Backup original features once.
    backup_path = processed_dir / "features_daily_original.csv"
    if not backup_path.exists():
        df.to_csv(backup_path, index=False)

    # Use only the last 30 percent of the dataset for synthetic anomalies.
    # This avoids contaminating the training part, because the model trains on the first 70%.
    split_idx = int(len(df) * 0.7)
    test_dates = df.iloc[split_idx:]["date"].tolist()

    selected = pick_dates(test_dates, 12)

    labels = pd.DataFrame({
        "date": df["date"],
        "y_true": 0,
        "anomaly_type": "normal"
    })

    if len(selected) < 4:
        raise ValueError("Not enough test dates to inject anomalies.")

    inactivity_dates = selected[0:3]
    night_dates = selected[3:6]
    missed_routine_dates = selected[6:9]
    sensor_failure_dates = selected[9:12]

    high_night = max(
        float(df["night_motion_count"].quantile(0.95)) * 1.8,
        float(df["night_motion_count"].max()) + 50
    )

    # 1. Severe inactivity anomaly.
    mask = df["date"].isin(inactivity_dates)
    df.loc[mask, "motion_count_total"] = 5
    df.loc[mask, "morning_motion_count"] = 0
    df.loc[mask, "day_motion_count"] = 0
    df.loc[mask, "evening_motion_count"] = 5
    df.loc[mask, "longest_inactivity_gap_minutes"] = 900
    labels.loc[labels["date"].isin(inactivity_dates), ["y_true", "anomaly_type"]] = [1, "synthetic_severe_inactivity"]

    # 2. Unusual nighttime movement.
    mask = df["date"].isin(night_dates)
    df.loc[mask, "night_motion_count"] = high_night
    labels.loc[labels["date"].isin(night_dates), ["y_true", "anomaly_type"]] = [1, "synthetic_unusual_night_movement"]

    # 3. Missed morning routine.
    mask = df["date"].isin(missed_routine_dates)
    df.loc[mask, "morning_motion_count"] = 0
    labels.loc[labels["date"].isin(missed_routine_dates), ["y_true", "anomaly_type"]] = [1, "synthetic_missed_morning_routine"]

    # 4. Sensor failure / missing data case.
    mask = df["date"].isin(sensor_failure_dates)
    df.loc[mask, "event_count"] = 0
    df.loc[mask, "motion_count_total"] = 0
    df.loc[mask, "door_event_count"] = 0
    df.loc[mask, "night_motion_count"] = 0
    df.loc[mask, "morning_motion_count"] = 0
    df.loc[mask, "day_motion_count"] = 0
    df.loc[mask, "evening_motion_count"] = 0
    df.loc[mask, "longest_inactivity_gap_minutes"] = 1440
    df.loc[mask, "active_sensors_count"] = 0
    df.loc[mask, "active_sensor_types_count"] = 0
    labels.loc[labels["date"].isin(sensor_failure_dates), ["y_true", "anomaly_type"]] = [1, "synthetic_sensor_failure"]

    df.to_csv(features_path, index=False)
    labels.to_csv(processed_dir / "labels.csv", index=False)

    print("Synthetic anomalies injected into data/processed/features_daily.csv")
    print("Ground-truth labels written to data/processed/labels.csv")
    print()
    print("Injected anomaly dates:")
    print("Severe inactivity:", inactivity_dates)
    print("Night movement:", night_dates)
    print("Missed routine:", missed_routine_dates)
    print("Sensor failure:", sensor_failure_dates)


if __name__ == "__main__":
    main()
