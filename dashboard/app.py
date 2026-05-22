from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Privacy-Aware Smart Home Monitoring", layout="wide")

st.title("Privacy-Aware Smart Home Routine Monitoring")
st.caption("Course prototype for daily routine anomaly detection using ambient sensor data.")

pred_path = Path("outputs/predictions_combined.csv")
metrics_path = Path("outputs/metrics.json")
features_path = Path("data/processed/features_daily.csv")

if not pred_path.exists():
    st.warning("No predictions found. Run the preprocessing and evaluation scripts first.")
    st.code("python scripts/01_prepare_dataset.py --input data/raw/demo_events.csv\npython scripts/02_train_evaluate.py")
    st.stop()

pred = pd.read_csv(pred_path)
pred["date"] = pd.to_datetime(pred["date"])
features = pd.read_csv(features_path) if features_path.exists() else pd.DataFrame()
if not features.empty:
    features["date"] = pd.to_datetime(features["date"])

latest = pred.sort_values("date").iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest rule score", f"{latest.get('rule_anomaly_score', 0):.2f}")
col2.metric("Latest ML score", f"{latest.get('iforest_anomaly_score', 0):.2f}")
col3.metric("Notification level", int(latest.get("notification_level", 0)))
col4.metric("Latest status", latest.get("rule_anomaly_type", "normal"))

st.subheader("Anomaly score timeline")
score_df = pred[["date", "rule_anomaly_score", "iforest_anomaly_score"]].melt(
    id_vars="date", var_name="model", value_name="score"
)
st.plotly_chart(px.line(score_df, x="date", y="score", color="model", markers=True), use_container_width=True)

st.subheader("Detected anomalies and notification policy")
show_cols = [
    "date",
    "rule_is_anomaly",
    "iforest_is_anomaly",
    "rule_anomaly_type",
    "notification_level",
    "notification_message",
]
if "y_true" in pred.columns:
    show_cols.extend(["y_true", "anomaly_type"])
st.dataframe(pred[show_cols].sort_values("date", ascending=False), use_container_width=True)

if not features.empty:
    st.subheader("Daily routine features")
    numeric_cols = [c for c in features.columns if c != "date" and pd.api.types.is_numeric_dtype(features[c])]
    default_cols = [c for c in ["motion_count_total", "night_motion_count", "longest_inactivity_gap_minutes"] if c in numeric_cols]
    selected = st.multiselect("Select features to plot", numeric_cols, default=default_cols[:3])
    if selected:
        plot_df = features[["date"] + selected].melt(id_vars="date", var_name="feature", value_name="value")
        st.plotly_chart(px.line(plot_df, x="date", y="value", color="feature", markers=True), use_container_width=True)

if metrics_path.exists():
    st.subheader("Evaluation metrics")
    with metrics_path.open("r", encoding="utf-8") as f:
        metrics = json.load(f)
    st.json(metrics)

st.info(
    "This dashboard is for a course prototype only. It reports routine deviations, not medical diagnoses or confirmed emergencies."
)
