#!/usr/bin/env bash
set -e
python scripts/01_prepare_dataset.py --input data/raw/aruba.csv
python scripts/04_make_synthetic_labels.py
python scripts/02_train_evaluate.py
python -m streamlit run dashboard/app.py
