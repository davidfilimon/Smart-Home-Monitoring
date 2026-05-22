from __future__ import annotations

from pathlib import Path
from typing import Optional
import pandas as pd


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common smart-home dataset column names."""
    rename_map = {}
    for col in df.columns:
        low = col.strip().lower()
        if low in {"sensor", "sensorid", "sensor_id", "sensor name", "sensor_name"}:
            rename_map[col] = "sensor_id"
        elif low in {"state", "value", "message", "status"}:
            rename_map[col] = "message"
        elif low in {"activity", "label", "activity_label"}:
            rename_map[col] = "activity"
        elif low in {"datetime", "date_time", "timestamp", "time_stamp"}:
            rename_map[col] = "timestamp"
        elif low == "date":
            rename_map[col] = "date"
        elif low == "time":
            rename_map[col] = "time"
    df = df.rename(columns=rename_map)
    return df


def read_casas_txt(path: str | Path) -> pd.DataFrame:
    """Read a CASAS-like whitespace-delimited text file.

    Expected line pattern:
    YYYY-MM-DD HH:MM:SS.ssssss SENSOR_ID MESSAGE [activity...]
    """
    rows = []
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            date, time, sensor_id, message = parts[:4]
            activity = " ".join(parts[4:]) if len(parts) > 4 else ""
            rows.append(
                {
                    "date": date,
                    "time": time,
                    "sensor_id": sensor_id,
                    "message": message,
                    "activity": activity,
                }
            )
    if not rows:
        raise ValueError(f"No valid rows parsed from {path}")
    return pd.DataFrame(rows)


def read_events(path: str | Path) -> pd.DataFrame:
    """Read CSV or CASAS TXT smart-home events and return normalized event data."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    if path.suffix.lower() in {".csv", ".tsv"}:
        sep = "\t" if path.suffix.lower() == ".tsv" else ","
        df = pd.read_csv(path, sep=sep)
        df = _normalize_columns(df)
    else:
        df = read_casas_txt(path)

    if "timestamp" not in df.columns:
        if {"date", "time"}.issubset(df.columns):
            df["timestamp"] = pd.to_datetime(
                df["date"].astype(str) + " " + df["time"].astype(str),
                errors="coerce",
            )
        else:
            raise ValueError("Input data must contain timestamp or date + time columns.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    required = ["timestamp", "sensor_id", "message"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if "activity" not in df.columns:
        df["activity"] = ""

    df = df.dropna(subset=["timestamp"]).copy()
    df["sensor_id"] = df["sensor_id"].astype(str).str.strip()
    df["message"] = df["message"].astype(str).str.strip().str.upper()
    df["activity"] = df["activity"].astype(str).str.strip()
    df["date"] = df["timestamp"].dt.date.astype(str)
    df["hour"] = df["timestamp"].dt.hour
    df["minute_of_day"] = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df[["timestamp", "date", "hour", "minute_of_day", "sensor_id", "message", "activity"]]


def infer_sensor_type(sensor_id: str) -> str:
    """Infer broad sensor type from common CASAS-style IDs."""
    sid = str(sensor_id).strip().upper()
    if sid.startswith("M"):
        return "motion"
    if sid.startswith("D"):
        return "door"
    if sid.startswith("T"):
        return "temperature"
    if sid.startswith("L"):
        return "light"
    if sid.startswith("I"):
        return "item"
    return "other"
