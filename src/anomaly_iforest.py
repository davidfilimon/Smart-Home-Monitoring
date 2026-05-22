from __future__ import annotations

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.features import numeric_feature_columns


def fit_iforest(train_df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[IsolationForest, StandardScaler, list[str]]:
    params = config.get("iforest", {})
    feature_cols = numeric_feature_columns(train_df)
    if not feature_cols:
        raise ValueError("No numeric feature columns available for Isolation Forest.")

    scaler = StandardScaler()
    x_train = scaler.fit_transform(train_df[feature_cols])

    model = IsolationForest(
        contamination=float(params.get("contamination", 0.08)),
        random_state=int(params.get("random_state", 42)),
    )
    model.fit(x_train)
    return model, scaler, feature_cols


def predict_iforest(df: pd.DataFrame, model: IsolationForest, scaler: StandardScaler, feature_cols: list[str]) -> pd.DataFrame:
    x = scaler.transform(df[feature_cols])
    pred = model.predict(x)  # -1 anomaly, 1 normal
    raw_score = -model.decision_function(x)  # higher = more anomalous

    # Normalize for dashboard readability.
    min_s, max_s = float(raw_score.min()), float(raw_score.max())
    if max_s > min_s:
        norm_score = (raw_score - min_s) / (max_s - min_s)
    else:
        norm_score = np.zeros_like(raw_score)

    return pd.DataFrame(
        {
            "date": df["date"].values,
            "iforest_is_anomaly": (pred == -1).astype(int),
            "iforest_anomaly_score": norm_score,
        }
    )
