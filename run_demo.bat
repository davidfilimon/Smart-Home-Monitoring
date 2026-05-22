@echo off
python scripts\03_generate_demo_data.py
python scripts\01_prepare_dataset.py --input data\raw\demo_events.csv
python scripts\02_train_evaluate.py
streamlit run dashboard\app.py
