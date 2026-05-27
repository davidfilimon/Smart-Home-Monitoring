import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
from src.load_data import read_events, read_casas_txt, infer_sensor_type, _normalize_columns


# --- Helpers ---

def write_csv(path, content):
    Path(path).write_text(content, encoding="utf-8")

def write_txt(path, content):
    Path(path).write_text(content, encoding="utf-8")


# --- infer_sensor_type ---

def test_infer_sensor_type_motion():
    assert infer_sensor_type("M001") == "motion"

def test_infer_sensor_type_door():
    assert infer_sensor_type("D002") == "door"

def test_infer_sensor_type_temperature():
    assert infer_sensor_type("T003") == "temperature"

def test_infer_sensor_type_light():
    assert infer_sensor_type("L004") == "light"

def test_infer_sensor_type_unknown():
    assert infer_sensor_type("X999") == "other"


# --- _normalize_columns ---

def test_normalize_columns_sensor_id():
    df = pd.DataFrame([{"sensor name": "M001", "state": "ON", "datetime": "2011-01-01 08:00:00"}])
    result = _normalize_columns(df)
    assert "sensor_id" in result.columns
    assert "message" in result.columns
    assert "timestamp" in result.columns

def test_normalize_columns_pastreaza_coloane_necunoscute():
    df = pd.DataFrame([{"sensor_id": "M001", "extra_col": "ceva"}])
    result = _normalize_columns(df)
    assert "extra_col" in result.columns


# --- read_casas_txt ---

def test_read_casas_txt_citeste_corect():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("2011-01-01 08:00:00.000 M001 ON Sleeping\n")
        f.write("2011-01-01 09:00:00.000 D002 OPEN\n")
        path = f.name
    try:
        df = read_casas_txt(path)
        assert len(df) == 2
        assert df.iloc[0]["sensor_id"] == "M001"
        assert df.iloc[0]["activity"] == "Sleeping"
        assert df.iloc[1]["activity"] == ""
    finally:
        os.unlink(path)

def test_read_casas_txt_ignora_comentarii():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# acesta e un comentariu\n")
        f.write("2011-01-01 08:00:00.000 M001 ON\n")
        path = f.name
    try:
        df = read_casas_txt(path)
        assert len(df) == 1
    finally:
        os.unlink(path)

def test_read_casas_txt_fisier_gol_arunca_eroare():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        path = f.name
    try:
        with pytest.raises(ValueError):
            read_casas_txt(path)
    finally:
        os.unlink(path)


# --- read_events ---

def test_read_events_fisier_inexistent_arunca_eroare():
    with pytest.raises(FileNotFoundError):
        read_events("fisier_care_nu_exista.csv")

def test_read_events_csv_returneaza_coloanele_corecte():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,sensor_id,message\n")
        f.write("2011-01-01,08:00:00,M001,ON\n")
        f.write("2011-01-01,09:00:00,D002,OPEN\n")
        path = f.name
    try:
        df = read_events(path)
        assert "timestamp" in df.columns
        assert "sensor_id" in df.columns
        assert "message" in df.columns
        assert "date" in df.columns
        assert "hour" in df.columns
        assert "minute_of_day" in df.columns
    finally:
        os.unlink(path)

def test_read_events_mesajele_sunt_uppercase():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,sensor_id,message\n")
        f.write("2011-01-01,08:00:00,M001,on\n")
        path = f.name
    try:
        df = read_events(path)
        assert df.iloc[0]["message"] == "ON"
    finally:
        os.unlink(path)

def test_read_events_sortat_dupa_timestamp():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,sensor_id,message\n")
        f.write("2011-01-01,10:00:00,M001,ON\n")
        f.write("2011-01-01,08:00:00,M002,ON\n")
        path = f.name
    try:
        df = read_events(path)
        assert df.iloc[0]["hour"] == 8
        assert df.iloc[1]["hour"] == 10
    finally:
        os.unlink(path)

def test_read_events_adauga_activity_goala_daca_lipseste():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,sensor_id,message\n")
        f.write("2011-01-01,08:00:00,M001,ON\n")
        path = f.name
    try:
        df = read_events(path)
        assert "activity" in df.columns
    finally:
        os.unlink(path)

def test_read_events_minute_of_day_corect():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,time,sensor_id,message\n")
        f.write("2011-01-01,08:30:00,M001,ON\n")
        path = f.name
    try:
        df = read_events(path)
        assert df.iloc[0]["minute_of_day"] == 8 * 60 + 30
    finally:
        os.unlink(path)