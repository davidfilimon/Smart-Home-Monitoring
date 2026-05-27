from __future__ import annotations

from pathlib import Path
import random
import pandas as pd

random.seed(42)

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

sensors = {
    "M001": "bedroom",
    "M002": "kitchen",
    "M003": "bathroom",
    "M004": "living_room",
    "D001": "entrance",
}

start = pd.Timestamp("2026-01-01")
rows = []
labels = []

anomaly_days = {
    45: "inactivity",
    50: "unusual_night_movement",
    55: "missed_morning_routine",
    58: "sensor_failure",
}

for day_idx in range(60):
    day = start + pd.Timedelta(days=day_idx)
    anomaly = anomaly_days.get(day_idx, "normal")
    labels.append({"date": str(day.date()), "y_true": 0 if anomaly == "normal" else 1, "anomaly_type": anomaly})

    if anomaly == "sensor_failure":
        # Almost no data. This tests the failure case.
        ts = day + pd.Timedelta(hours=12, minutes=0)
        rows.append({"timestamp": ts, "sensor_id": "M004", "message": "ON", "activity": "Unknown"})
        continue

    # Normal morning routine: bedroom -> bathroom -> kitchen -> entrance/living.
    morning_events = [
        (7, 10, "M001", "ON", "Wake_Up"),
        (7, 25, "M003", "ON", "Bathroom"),
        (7, 55, "M002", "ON", "Breakfast"),
        (8, 20, "D001", "OPEN", "Leave_Home"),
    ]

    if anomaly == "missed_morning_routine":
        morning_events = [(7, 10, "M001", "ON", "Wake_Up")]

    for h, m, sensor, msg, activity in morning_events:
        jitter = random.randint(-5, 5)
        ts = day + pd.Timedelta(hours=h, minutes=m + jitter)
        rows.append({"timestamp": ts, "sensor_id": sensor, "message": msg, "activity": activity})

    # Daytime activity.
    daytime_count = 25 if anomaly != "inactivity" else 3
    for _ in range(daytime_count):
        h = random.randint(9, 20)
        m = random.randint(0, 59)
        sensor = random.choice(["M002", "M003", "M004", "D001"])
        msg = "OPEN" if sensor.startswith("D") else "ON"
        ts = day + pd.Timedelta(hours=h, minutes=m)
        rows.append({"timestamp": ts, "sensor_id": sensor, "message": msg, "activity": "Daily_Activity"})

    # Evening routine.
    for h, m, sensor, activity in [(21, 30, "M004", "Relax"), (22, 30, "M001", "Sleep")]:
        ts = day + pd.Timedelta(hours=h, minutes=m + random.randint(-10, 10))
        rows.append({"timestamp": ts, "sensor_id": sensor, "message": "ON", "activity": activity})

    # Night anomaly: many movements at night.
    if anomaly == "unusual_night_movement":
        for _ in range(18):
            h = random.randint(0, 4)
            m = random.randint(0, 59)
            sensor = random.choice(["M001", "M003", "M004"])
            ts = day + pd.Timedelta(hours=h, minutes=m)
            rows.append({"timestamp": ts, "sensor_id": sensor, "message": "ON", "activity": "Night_Movement"})

out = pd.DataFrame(rows).sort_values("timestamp")
out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
out.to_csv(RAW_DIR / "demo_events.csv", index=False)
pd.DataFrame(labels).to_csv(PROCESSED_DIR / "labels.csv", index=False)

print("Demo data written to data/raw/demo_events.csv")
print("Demo labels written to data/processed/labels.csv")
