from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config import load_config
from src.load_data import read_events
from src.privacy import make_privacy_feature_sets


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare smart-home dataset features.")
    parser.add_argument("--input", default="data/raw/casas_aruba.txt", help="Path to raw dataset file.")
    parser.add_argument("--config", default="config.json", help="Path to config JSON.")
    args = parser.parse_args()

    config = load_config(args.config)
    events = read_events(args.input)

    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    events.to_csv(processed_dir / "events_normalized.csv", index=False)
    feature_sets = make_privacy_feature_sets(events, config)

    for name, df in feature_sets.items():
        df.to_csv(processed_dir / f"features_{name}.csv", index=False)

    # Default feature file for training/evaluation.
    feature_sets["P0_raw_derived"].to_csv(processed_dir / "features_daily.csv", index=False)

    print(f"Parsed events: {len(events)}")
    print("Feature files written to data/processed/")


if __name__ == "__main__":
    main()
