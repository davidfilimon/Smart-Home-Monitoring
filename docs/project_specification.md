# Integrated Project Specification

## Project title

Project 35 - Privacy-Aware Smart Home Monitoring for Daily Routine Anomaly Detection

## Objective

Build a privacy-aware ambient sensing framework that models a resident's daily routine and detects deviations such as inactivity, unusual nighttime movement, missed routines and sensor failure cases.

## Input data

The system uses simulated or public ambient smart-home sensor events. Each event contains:

- timestamp
- sensor identifier
- sensor message/state
- optional activity label

No video, audio, biometric or personally identifying data is required.

## Produced output

The system produces:

- daily feature vectors
- anomaly score
- anomaly flag
- interpreted anomaly type
- notification level
- dashboard visualization
- evaluation report

## Assumptions

- The resident has a relatively stable daily routine.
- Ambient sensors provide indirect evidence of activity.
- The system is not medically validated.
- The prototype does not infer exact health status.

## System boundaries

Included:

- public/simulated data
- routine modeling
- anomaly detection
- privacy transformations
- dashboard
- caregiver notification policy

Excluded:

- real deployment in private homes
- surveillance of third parties
- camera or microphone monitoring
- clinical decision support
- emergency service automation

## Threat model

Potential privacy risks:

- exact timestamp exposure
- room-level behavior inference
- sensitive routine pattern leakage
- excessive raw event retention

Mitigations:

- data minimization
- sensor pseudonymization
- temporal aggregation
- daily feature extraction
- careful notification wording
