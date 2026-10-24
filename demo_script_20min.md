# GlucoTwin Demo Recording Script — 20 Minutes

**Recording requirement:** The challenge listing requests a minimum 20-minute demonstration video. This file is a timing guide, not a recorded video. Record the screen and narration, upload in the accepted format (for example, an unlisted video), test the link in a private/incognito browser, and replace the video-link placeholder in `README.md`.

## Before recording (not part of the 20 minutes)

- Run `pip install -r requirements.txt` and then `streamlit run app/app.py`.
- Open the dashboard in a browser at the local Streamlit URL.
- Open `app/twin_model.py`, `generate_synthetic_data.py`, `docs/architecture.pdf`, and `docs/presentation.pdf` in separate windows.
- Use only the bundled synthetic data. Do not show personal information or secrets.
- Record at 1080p if possible; ensure the dashboard and terminal text are readable.

## Timed narration and demonstration

### 00:00–01:30 — Introduce the use case (1.5 min)

"This project is GlucoTwin, a narrow proof of concept for the Happiest Health Digital Twin Challenge. It fuses static EHR context with hourly synthetic wearable signals and forecasts whether the simulated glucose reading will reach at least 180 mg/dL two hours ahead. Everything in this demo is synthetic; it is not a clinical tool."

### 01:30–03:30 — Problem and why the twin is dynamic (2 min)

Explain that a static EHR alone does not represent the current state. The prototype combines long-term context such as HbA1c and diabetes duration with current CGM, heart rate, HRV, sleep, steps and logged meal carbohydrates. Emphasize the bounded use case rather than claiming a complete human digital twin.

### 03:30–05:30 — Architecture and data flow (2 min)

Show `docs/architecture.pdf`. Explain patient ID joins, hourly feature assembly, the retrospective two-hour target used for training, the patient-level holdout, and the probability passed to the dashboard. State that the target is not passed into the model features.

### 05:30–08:00 — Synthetic data and privacy (2.5 min)

Open `data/synthetic_ehr.csv` and `data/synthetic_wearable_hourly.csv`. Point out fake IDs (`GT-...`), synthetic timestamps and generated values. Explain that there are 320 simulated profiles, seven days per profile, 53,760 sensor windows and 53,120 two-hour labels. No real patient records or external APIs are used.

### 08:00–11:00 — Live dashboard tour (3 min)

Show the patient profile and selected timestamp. Explain the EHR panel, current wearable metrics and 24-hour glucose/activity plots. Move the replay-hour slider to show the virtual patient evolving over time. Call out that the 180 mg/dL line is an illustrative target reference, not a medical recommendation.

### 11:00–13:30 — What-if scenario (2.5 min)

Change the simulated current glucose, carbohydrates, steps and sleep using sidebar controls. Compare the original and scenario probability. Explain that this is sensitivity exploration only, not an intervention simulator; it does not recommend medicine, diet, or activity.

### 13:30–16:00 — Model and evaluation (2.5 min)

Open `app/twin_model.py` and point out the Random Forest, feature list, patient-level split and scoring code. Explain ROC-AUC, average precision, precision and recall at the demo threshold. Show that test patients do not overlap the training patient IDs. Note that synthetic-only metrics are optimistic by construction and do not generalize to clinical care.

### 16:00–18:00 — Safety, limitations and next steps (2 min)

Cover external validation, calibration, subgroup analysis, prospective evaluation, clinical review, governance and privacy review. Explain that feature importance is not causal and the model is not clinically validated.

### 18:00–19:15 — Repository tour (1.25 min)

Show README, requirements, generator, tests, model card, data dictionary, MIT License, architecture PDF/PPTX, presentation PDF/PPTX and this script. Confirm a clean install and launch command.

### 19:15–20:00 — Close (45 sec)

"GlucoTwin demonstrates a reproducible, synthetic-data pipeline for joining historical context with dynamic sensor data and exposing a forecast in a clinician-oriented interface. The next milestone is independent validation on appropriately governed real-world data before making any claims about clinical utility. Thank you."

## Upload checklist

- [ ] Video lasts at least 20 minutes and includes narration plus working prototype screen.
- [ ] Dashboard is visible and interaction is demonstrated.
- [ ] Architecture, model, data provenance, validation and safety limits are discussed.
- [ ] Video link opens for anyone with the link; no login requirement for evaluators.
- [ ] Public repository README includes the final video URL.
