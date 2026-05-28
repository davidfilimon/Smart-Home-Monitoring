# Privacy-Aware Smart Home Monitoring for Daily Routine Anomaly Detection

Course prototype pentru detectarea anomaliilor de rutina zilnica folosind date ambientale smart-home, cu accent pe **data minimization**, **privacy-by-design**, **false-positive analysis** si **caregiver notification policy**.

Proiectul foloseste date publice de tip CASAS/Aruba sau CSV-uri similare cu evenimente smart-home.

---

## 1. Ce face proiectul

Sistemul transforma evenimente smart-home in feature-uri zilnice si detecteaza abateri precum:

- inactivitate severa;
- miscare neobisnuita noaptea;
- rutina de dimineata ratata;
- date lipsa / posibil senzor defect;
- alerte cu niveluri diferite pentru caregiver.

Dashboard-ul Streamlit afiseaza:

- latest rule score;
- latest ML score;
- notification level;
- latest status;
- anomaly score timeline;
- tabel cu zile normale/anormale;
- daily routine features;
- evaluation metrics.

---

## 2. Structura proiectului

```text
privacy-aware-smart-home-monitoring/
|
|-- config.json
|-- requirements.txt
|-- README.md
|
|-- data/
|   |-- raw/                  # aici pui datasetul real, ex. aruba.csv
|   |-- processed/            # fisiere generate automat
|
|-- src/
|   |-- load_data.py          # parser CASAS CSV/TXT
|   |-- features.py           # feature extraction
|   |-- privacy.py            # privacy levels
|   |-- anomaly_rules.py      # rule-based anomaly detector
|   |-- anomaly_iforest.py    # Isolation Forest model
|   |-- evaluation.py         # metrics
|   |-- notification_policy.py
|
|-- scripts/
|   |-- 01_prepare_dataset.py
|   |-- 02_train_evaluate.py
|   |-- 03_generate_demo_data.py
|   |-- 04_make_synthetic_labels.py
|
|-- dashboard/
|   |-- app.py
|
|-- docs/
|   |-- caregiver_policy.md
|   |-- privacy_design.md
|   |-- project_specification.md
|
|-- reports/
|   |-- dataset_protocol.md
|   |-- evaluation_report_template.md
|   |-- ieee_paper_template.md
|   |-- project_documentation.pdf
|
|-- outputs/
    |-- predictions_combined.csv
    |-- metrics.json
```

---

## 3. Dataset recomandat

Alegerea recomandata este **CASAS Dataset 11 - Aruba**:

```text
Dataset: Aruba
Residents: 1
Description: Daily life, 2010-2011
Annotated: Yes
```

Este potrivit pentru tema deoarece are un singur rezident, activitate zilnica si evenimente de la senzori ambientali. Formatul gasit in CSV poate arata asa:

```csv
2010-11-04,00:03:50.209589,Bedroom,ON
2010-11-04,00:03:57.399391,Bedroom,OFF
2010-11-04,02:32:33.351906,Bedroom,ON
2010-11-04,02:32:38.895958,Bedroom,OFF
```

Proiectul suporta fisiere CSV fara header. Totusi, pentru claritate, poti face si o copie cu header:

```bash
printf "date,time,sensor_id,message\n" > data/raw/aruba_fixed.csv
cat data/raw/aruba.csv >> data/raw/aruba_fixed.csv
```

---

## 4. Instalare pe CachyOS / Arch-based Linux

Din folderul proiectului:

```bash
sudo pacman -Syu
sudo pacman -S python python-pip

cd ~/privacy-aware-smart-home-monitoring
python -m venv .venv
source .venv/bin/activate.fish

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Daca `venv` da eroare:

```bash
sudo pacman -S python-virtualenv
python -m venv .venv
source .venv/bin/activate.fish
```

Pentru fish shell, activarea corecta este:

```bash
source .venv/bin/activate.fish
```

Nu folosi varianta clasica `source .venv/bin/activate`, fiindca aceea este pentru bash/zsh.

---

## 5. Rulare cu dataset real Aruba

Pune datasetul in:

```text
data/raw/aruba.csv
```

Apoi ruleaza:

```bash
rm -rf outputs/*
rm -rf data/processed/*

python scripts/01_prepare_dataset.py --input data/raw/aruba.csv
python scripts/02_train_evaluate.py
python -m streamlit run dashboard/app.py
```

Daca folosesti copia cu header:

```bash
python scripts/01_prepare_dataset.py --input data/raw/aruba_fixed.csv
python scripts/02_train_evaluate.py
python -m streamlit run dashboard/app.py
```

---

## 6. Rulare completa cu anomalii sintetice si metrici

Datasetul Aruba nu are o coloana directa `y_true` pentru anomalii. De aceea, pentru evaluare reproducibila, proiectul injecteaza controlat anomalii sintetice in partea de test.

Ruleaza:

```bash
rm -rf outputs/*
rm -rf data/processed/*

python scripts/01_prepare_dataset.py --input data/raw/aruba.csv
python scripts/04_make_synthetic_labels.py
python scripts/02_train_evaluate.py
python -m streamlit run dashboard/app.py
```

Dupa acest pas, in dashboard trebuie sa apara metrici precum:

```text
accuracy
precision
recall
f1
confusion_matrix
```

---

## 7. Privacy design

Proiectul compara mai multe niveluri de prelucrare a datelor:

| Nivel | Descriere | Privacy | Utilitate |
|---|---|---:|---:|
| P0 | raw-derived daily features | scazuta | mare |
| P1 | sensor pseudonymization | medie | mare |
| P2 | hourly aggregated features | buna | medie-mare |
| P3 | daily minimized features | foarte buna | medie |

Ideea principala: sistemul nu are nevoie de camera, microfon sau date brute permanente. Detectia se poate face pe feature-uri agregate precum:

```text
event_count
motion_count_total
night_motion_count
morning_motion_count
longest_inactivity_gap_minutes
active_sensors_count
```

---

## 8. Modele folosite

### 8.1 Rule-based detector

Detectorul pe reguli foloseste praguri invatate din perioada initiala considerata normala:

- valori mici pentru `event_count` pot indica date lipsa;
- valori mari pentru `night_motion_count` pot indica miscare nocturna neobisnuita;
- valori mici pentru `morning_motion_count` pot indica rutina de dimineata ratata;
- valori mari pentru `longest_inactivity_gap_minutes` pot indica inactivitate.

Avantaj: usor de explicat si bun pentru safety escalation.

Dezavantaj: produce mai multe false positives.

### 8.2 Isolation Forest

Modelul ML este nesupervizat si invata distributia zilelor normale. Zilele care ies din distributie primesc scor de anomalie mai mare.

Avantaj: reduce unele false positives.

Dezavantaj: poate rata anomalii sintetice daca acestea nu sunt suficient de diferite statistic.

---

## 9. Rezultate obtinute pe Aruba + anomalii sintetice

Rezultatele obtinute dupa eliminarea data leakage-ului (`y_true` nu mai este folosit ca feature):

### Rule-based model

```text
accuracy  = 0.818
precision = 0.231
recall    = 1.000
f1        = 0.375
TN = 168
FP = 40
FN = 0
TP = 12
```

Interpretare:

- detecteaza toate cele 12 anomalii sintetice;
- nu are false negatives;
- produce 40 false positives;
- este un model conservator, potrivit ca safety baseline.

### Isolation Forest

```text
accuracy  = 0.877
precision = 0.222
recall    = 0.500
f1        = 0.308
TN = 187
FP = 21
FN = 6
TP = 6
```

Interpretare:

- are accuracy mai mare;
- produce mai putine false positives;
- rateaza 6 din 12 anomalii;
- este util ca semnal suplimentar, dar nu ca singur mecanism de alerta.

---

## 10. Interpretarea corecta pentru raport

Concluzia recomandata:

```text
The rule-based detector achieved perfect recall on the synthetic anomaly scenarios, detecting all injected anomalies, but produced a higher number of false positives. This behavior is acceptable as a conservative safety baseline in an Ambient Assisted Living context, where missing severe inactivity may be more harmful than generating a soft alert.

The Isolation Forest model achieved higher overall accuracy and fewer false positives, but missed several injected anomalies. Therefore, the prototype uses rule-based detection for safety-critical escalation and treats the ML anomaly score as an additional decision-support signal rather than a standalone emergency detector.
```

---

## 11. Caregiver notification policy

Nivelurile de notificare sunt:

```text
Level 0 - normal
No notification.

Level 1 - minor anomaly
Shown in dashboard as a soft alert.

Level 2 - repeated or moderate anomaly
Optional caregiver notification.

Level 3 - severe inactivity or missing-data pattern
Urgent caregiver notification.
```

Important: sistemul nu spune ca persoana a cazut sau ca exista o urgenta medicala confirmata. Sistemul spune doar ca exista o abatere de rutina.

Formulare corecta:

```text
Unusual inactivity detected compared to the resident's normal routine.
```

Formulare de evitat:

```text
The resident has fallen.
```

---

## 12. Ce screenshot-uri merita puse in raport

1. Dashboard overview:
   - Latest rule score;
   - Latest ML score;
   - Notification level;
   - Latest status.

2. Tabelul de anomalii:
   - normal;
   - unusual_night_movement;
   - severe_inactivity;
   - notification_level.

3. Evaluation metrics JSON:
   - accuracy;
   - precision;
   - recall;
   - F1;
   - confusion matrix.

4. Daily routine features graph:
   - motion_count_total;
   - night_motion_count;
   - longest_inactivity_gap_minutes.

---

## 13. Limitari

- Datasetul este public si nu reprezinta o validare clinica.
- Anomaliile sunt sintetice, injectate controlat pentru evaluare.
- Sistemul nu detecteaza diagnostic medical.
- Nu confirma caderi sau urgente reale.
- Performanta depinde de calitatea senzorilor si de stabilitatea rutinei.
- Nu trebuie folosit ca sistem de productie fara validare suplimentara.

---

## 14. Comanda scurta finala

Pentru rularea finala pe Aruba:

```bash
source .venv/bin/activate.fish
rm -rf outputs/* data/processed/*
python scripts/01_prepare_dataset.py --input data/raw/aruba.csv
python scripts/04_make_synthetic_labels.py
python scripts/02_train_evaluate.py
python -m streamlit run dashboard/app.py
```

Daca folosesti fisierul cu header:

```bash
python scripts/01_prepare_dataset.py --input data/raw/aruba_fixed.csv
```
