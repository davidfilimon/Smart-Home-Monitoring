from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


def merge_labels(predictions: pd.DataFrame, labels_path: str | Path = "data/processed/labels.csv") -> pd.DataFrame:
    labels_path = Path(labels_path)
    if not labels_path.exists():
        return predictions
    labels = pd.read_csv(labels_path)
    labels["date"] = labels["date"].astype(str)
    if "y_true" not in labels.columns:
        raise ValueError("labels.csv must contain a y_true column")
    return predictions.merge(labels, on="date", how="left")


def compute_metrics(df: pd.DataFrame, pred_col: str) -> Dict[str, Any]:
    if "y_true" not in df.columns or df["y_true"].isna().all():
        return {"status": "no_ground_truth", "message": "No y_true labels available. Metrics were not computed."}

    usable = df.dropna(subset=["y_true", pred_col]).copy()
    y_true = usable["y_true"].astype(int)
    y_pred = usable[pred_col].astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix_labels": ["normal", "anomaly"],
        "confusion_matrix": cm,
        "n_samples": int(len(usable)),
    }


def save_metrics(metrics: Dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
