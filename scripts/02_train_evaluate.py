from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.anomaly_iforest import fit_iforest, predict_iforest
from src.anomaly_rules import fit_rule_thresholds, predict_rules
from src.config import load_config
from src.evaluation import compute_metrics, merge_labels, save_metrics
from src.notification_policy import apply_notification_policy


def train_test_split_by_time(
    df: pd.DataFrame, train_ratio: float = 0.7
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = df.sort_values("date").reset_index(drop=True)
    split_idx = max(1, int(len(df) * train_ratio))
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def main() -> None:
    config = load_config("config.json")
    processed_dir = Path("data/processed")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    features_path = processed_dir / "features_daily.csv"
    if not features_path.exists():
        raise FileNotFoundError("Run scripts/01_prepare_dataset.py first.")

    features = pd.read_csv(features_path)
    features["date"] = features["date"].astype(str)

    labeled = merge_labels(features, processed_dir / "labels.csv")

    # If labels exist, train mostly on known normal days from early period.
    train_df, test_df = train_test_split_by_time(labeled, train_ratio=0.7)
    if "y_true" in train_df.columns:
        normal_train = train_df[train_df["y_true"].fillna(0).astype(int) == 0].copy()
        if len(normal_train) >= 5:
            train_df = normal_train

    thresholds = fit_rule_thresholds(train_df, config)
    rule_pred = predict_rules(labeled, thresholds)

    forbidden_features = [
        "y_true",
        "anomaly_type",
        "rule_is_anomaly",
        "iforest_is_anomaly",
        "rule_score",
        "ml_score",
        "notification_level",
        "rule_anomaly_type",
    ]

    train_for_model = train_df.drop(
        columns=[c for c in forbidden_features if c in train_df.columns],
        errors="ignore",
    )

    labeled_for_model = labeled.drop(
        columns=[c for c in forbidden_features if c in labeled.columns],
        errors="ignore",
    )

    model, scaler, feature_cols = fit_iforest(train_for_model, config)

    feature_cols = [
        c for c in feature_cols if c not in forbidden_features and c != "date"
    ]

    iforest_pred = predict_iforest(labeled_for_model, model, scaler, feature_cols)

    predictions = (
        labeled[["date"]]
        .merge(rule_pred, on="date", how="left")
        .merge(iforest_pred, on="date", how="left")
    )
    if "y_true" in labeled.columns:
        predictions = predictions.merge(
            labeled[["date", "y_true", "anomaly_type"]], on="date", how="left"
        )

    predictions = apply_notification_policy(predictions)
    predictions.to_csv(outputs_dir / "predictions_combined.csv", index=False)

    metrics = {
        "rule_based": compute_metrics(predictions, "rule_is_anomaly"),
        "isolation_forest": compute_metrics(predictions, "iforest_is_anomaly"),
        "used_features": feature_cols,
        "rule_thresholds": thresholds,
    }
    save_metrics(metrics, outputs_dir / "metrics.json")

    print("Predictions written to outputs/predictions_combined.csv")
    print("Metrics written to outputs/metrics.json")


if __name__ == "__main__":
    main()
