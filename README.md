# GlucoTwin — Synthetic Digital Twin Proof of Concept

> **Happiest Health Digital Twin Challenge 2026 | Research prototype | Synthetic data only**

GlucoTwin demonstrates a narrow, explainable-in-context digital-twin workflow: join a patient's static Electronic Health Record (EHR) profile with hourly consumer-wearable/continuous-glucose-monitoring (CGM) signals, then estimate the probability that their synthetic glucose value will be **at least 180 mg/dL two hours later**. A Streamlit dashboard lets a reviewer replay virtual patients and change selected sensor readings in a clearly labeled *what-if* scenario.

**Not for clinical use.** This is a challenge proof of concept, not a medical device, validated clinical decision support system, diagnosis, or treatment recommendation. All data and all reported metrics are synthetic. Do not enter real patient information.

## Challenge submission details — replace before publishing

- **Team name:** `[ENTER TEAM NAME]`
- **Team members:** `[ENTER FULL NAMES]`
- **College / incubator:** `[ENTER COLLEGE OR INCUBATOR]`
- **Team leader:** `[ENTER TEAM LEADER]`
- **Contact:** submit the leader's phone and email privately through the official submission platform; do not commit personal contact information to this repository unless your team chooses to publish it.
- **Project title:** GlucoTwin — Patient-specific 2-hour Glucose Spike Forecasting with EHR + Wearable Fusion
- **Repository URL:** `[PASTE PUBLIC GITHUB URL AFTER PUBLISHING]`
- **Prototype demonstration video (minimum 20 minutes):** `[PASTE UNLISTED VIDEO URL AFTER RECORDING]`

The challenge asks for team/college information, problem statement, technical stack, an accessible public GitHub repository, an architecture PDF/PPT, a presentation PDF/PPT, and a demonstration video of at least 20 minutes. The deck and architecture diagram are in `docs/`. A timed recording script is supplied in `docs/demo_script_20min.md`; a video itself has **not** been recorded by this project generator and its link must be added after the team records and uploads it.

## Problem statement and use case

Glucose patterns can change with recent glucose trajectory, meals, movement, sleep, and long-term patient context. The PoC explores whether a model can combine historical EHR attributes with live-like wearable readings to flag a possible high glucose value two hours ahead in a synthetic Type 2 diabetes cohort.

**Prediction target:** `synthetic CGM(t + 2 hours) >= 180 mg/dL`.

This target is used only to exercise a predictive pipeline. It is not a diagnostic definition, clinical threshold recommendation, or claim of real-world medical performance.

## What is included

- `app/app.py` — Streamlit dashboard with synthetic patient selector, 7-day replay, current-state metrics, 2-hour probability estimate, threshold control, what-if sensor controls, CGM/activity charts, model metrics, and feature-importance visualization.
- `app/twin_model.py` — reproducible EHR/wearable fusion, patient-level train/test split, Random Forest training, evaluation and artifact export.
- `generate_synthetic_data.py` — deterministic data generator (seed `20261024`).
- `data/synthetic_ehr.csv` — one EHR profile per synthetic patient.
- `data/synthetic_wearable_hourly.csv` — hourly synthetic sensor/activity records.
- `data/synthetic_labels_2h.csv` — retrospective target values aligned to each window and observed two hours later.
- `models/` — fitted model bundle and evaluation metrics from the included synthetic data.
- `docs/architecture.pdf` and `docs/architecture.pptx` — architecture diagram.
- `docs/presentation.pdf` and `docs/presentation.pptx` — project presentation deck.
- `docs/model_card.md`, `docs/data_dictionary.md`, and `docs/demo_script_20min.md` — limitations, data dictionary, and timed demo outline.
- `LICENSE` — MIT License.

## Architecture

```text
Synthetic EHR profile ─┐
                       ├─ join on patient_id ─ feature assembly ─ Random Forest ─ P(spike in 2 h)
Synthetic wearable ────┘          │                    │                            │
  hourly CGM, HR, HRV, steps,      └─ retrospective target from CGM at t+2 h      └─ Streamlit clinician view
  sleep, logged carbohydrates                    │
                                      patient-level holdout evaluation
```

See the full diagram in [`docs/architecture.pdf`](docs/architecture.pdf).

## Technical stack

- Python 3.10+ (tested by project generation on Python 3.13 environment)
- pandas and NumPy for data handling and synthetic generation
- scikit-learn RandomForestClassifier for modelling and evaluation
- Streamlit for the interactive dashboard
- Plotly for time-series and feature-importance plots
- joblib for serializing the model bundle

## Run locally

### 1. Create an environment and install dependencies

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Launch the dashboard

From the repository root:

```bash
streamlit run app/app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. On first launch, the app trains and caches the model using the included synthetic CSVs. It does not call external APIs and does not need API keys.

### 3. Regenerate data or retrain the model

```bash
python generate_synthetic_data.py
python app/twin_model.py
```

The training command writes `models/glucotwin_rf.joblib` and `models/evaluation_metrics.json`.

### 4. Run tests

```bash
pytest -q
```

## Model and validation

The model is a Random Forest classifier trained on 75% of patients and evaluated on the remaining 25% **by patient ID**, keeping all time windows from a patient within a single split. The target is the next observed synthetic CGM value two hours later being at least 180 mg/dL. Sensor values at `t+2` and all target columns are not included as prediction features.

| Synthetic holdout metric | Result |
|---|---:|
| Patients | 320 total; 240 train / 80 test |
| Labeled windows | 53,120 total; 39,840 train / 13,280 test |
| Event prevalence in test split | 46.0% |
| ROC-AUC | 0.967 |
| Average precision (PR-AUC summary) | 0.961 |
| Accuracy at threshold 0.50 | 0.898 |
| Precision at threshold 0.50 | 0.865 |
| Recall at threshold 0.50 | 0.923 |
| F1 at threshold 0.50 | 0.893 |

These numbers summarize performance on data generated by this repository's own simulator. They are **not evidence of clinical accuracy**; synthetic regularities can produce optimistic metrics. External validation on real, appropriately governed datasets, prospective evaluation, calibration, subgroup analysis, and clinical review are all missing.

## Privacy, safety, and responsible use

- The generator creates synthetic records; no real medical records or personal identifiers are included.
- Do not upload patient data to this repository or use the dashboard for care decisions.
- A threshold crossing is labeled a *model signal*, not a diagnosis or instruction.
- Feature importance is a model diagnostic, not a causal explanation.
- The prototype has not been clinically validated and is not intended for diagnosis, prevention, monitoring, prediction, prognosis, treatment, or alleviation of disease in a real patient.

## Repository publishing checklist

1. Replace all `[ENTER ...]` / `[PASTE ...]` placeholders in this README.
2. Rename the local folder to the challenge-required format: `Team Name_College Name`.
3. Keep the repository **Public** and verify that all links and files can be opened without authentication.
4. Upload `docs/architecture.pdf` and `docs/presentation.pdf` (PPTX files are also included for editing).
5. Record a continuous or clearly structured **minimum 20-minute** walkthrough using `docs/demo_script_20min.md`, upload it as an unlisted video or accepted format, and add its accessible link above.
6. Review your institution's policy on AI-assisted work and disclose usage if required. Review and understand every file before submission.
7. Submit only the team leader's name, phone number, email ID, and public GitHub repository link on the challenge platform, as directed by the organizer.

## License

Released under the MIT License; see [`LICENSE`](LICENSE).

## Challenge reference

Happiest Health Digital Twin Challenge 2026 listing: https://api.unstop.com/hackathons/digital-twin-challenge-2026-happiest-health-1757873
