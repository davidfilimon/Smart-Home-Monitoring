# Privacy-by-Design Notes

## Privacy goal

Detect routine anomalies while collecting the minimum amount of sensitive data needed for the task.

## Data minimization

The prototype avoids cameras, microphones, exact location tracking, biometric data and personal messages. It uses ambient sensor events only.

## Privacy levels

### P0 - Raw-derived features

Uses exact timestamp and exact sensor events before converting them to daily features. Highest detection utility, lowest privacy.

### P1 - Pseudonymized sensors

Replaces sensor identifiers with anonymous codes such as S001, S002. Reduces direct semantic exposure but still keeps event-level structure.

### P2 - Hourly aggregation

Stores counts per hour and broad sensor type. Reduces timestamp precision and makes reconstruction of exact behavior harder.

### P3 - Daily minimized features

Keeps only a small set of daily routine statistics. Best privacy, but may reduce detection quality.

## Data retention

For a real deployment, raw events should be discarded after feature extraction unless there is a clear, lawful and documented reason to retain them.

## Claims limitation

The system detects deviations from routine. It does not diagnose medical problems and does not prove that a fall or emergency occurred.
