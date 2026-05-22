# Dataset Protocol

## Dataset source

Recommended dataset: CASAS Aruba or another public smart-home ambient sensor dataset.

## Data type

The system uses event-based ambient sensor data:

- motion sensor events
- door sensor events
- optional temperature/light/item events
- timestamps
- optional activity labels

## Excluded data

The project does not use:

- video
- audio
- biometric data
- exact identity data
- third-party surveillance data

## Preprocessing steps

1. Parse raw TXT/CSV data.
2. Normalize timestamp, sensor ID and sensor message columns.
3. Infer broad sensor type from sensor ID.
4. Sort events by timestamp.
5. Extract daily and hourly features.
6. Apply privacy transformations.

## Train/test protocol

The default split is chronological:

- first 70% of days for training
- last 30% of days for testing/evaluation

If ground-truth labels exist, training should use normal days only when possible.

## Synthetic anomalies

If no real anomaly labels are available, controlled synthetic anomalies may be injected:

- inactivity: reduce daytime motion events
- unusual nighttime movement: increase motion events between 00:00 and 05:00
- missed routine: remove expected morning activity
- sensor failure: remove most or all events from a sensor/day

## Reproducibility

All preprocessing and model steps should be run through scripts in the `scripts/` folder.
