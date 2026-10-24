"""Generate deterministic, fully synthetic EHR and wearable data for GlucoTwin.

No real patient records are used. Seeded output is reproducible for a demo.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEED = 20261024
N_PATIENTS = 320
DAYS = 7


def generate():
    rng = np.random.default_rng(SEED)
    DATA.mkdir(parents=True, exist_ok=True)
    ehr_rows, wearable_rows, label_rows = [], [], []
    start = pd.Timestamp("2026-09-15 00:00:00")

    for p in range(1, N_PATIENTS + 1):
        pid = f"GT-{p:04d}"
        age = int(rng.integers(35, 80))
        sex = str(rng.choice(["Female", "Male"]))
        bmi = float(np.clip(rng.normal(28.3, 4.4), 19.0, 42.0))
        years_dx = int(rng.integers(1, 21))
        hba1c = float(np.clip(rng.normal(7.9 + 0.025 * (years_dx - 8), 1.05), 6.0, 11.8))
        hypertension = int(rng.random() < 0.43)
        metformin = int(rng.random() < 0.72)
        medication_adherence = float(np.clip(rng.beta(5.5, 2.0), 0.25, 1.0))
        family_history = int(rng.random() < 0.48)
        ehr_rows.append({
            "patient_id": pid, "age_years": age, "sex": sex, "bmi_kg_m2": round(bmi, 1),
            "diabetes_duration_years": years_dx, "hba1c_percent": round(hba1c, 2),
            "hypertension_flag": hypertension, "metformin_flag": metformin,
            "medication_adherence_0_1": round(medication_adherence, 3),
            "family_history_flag": family_history,
        })

        baseline = 98 + 10.2 * (hba1c - 7.0) + 0.58 * (bmi - 27) + 1.7 * years_dx / 10
        # Build a continuous one-hour sensor stream for 7 days.
        glucose_hist = []
        patient_wear_rows = []
        daily_sleep = {}
        for t in range(DAYS * 24):
            ts = start + pd.Timedelta(hours=t)
            hour = ts.hour
            day = t // 24
            if day not in daily_sleep:
                daily_sleep[day] = float(np.clip(rng.normal(6.8 - 0.012 * (age - 50), 1.0), 4.0, 9.5))
            sleep_hours = daily_sleep[day]
            # The food log is noisily simulated; heavier eating tends to occur at meal times.
            if hour in range(7, 10):
                carbs = float(np.clip(rng.normal(27, 13), 0, 72))
            elif hour in range(12, 15):
                carbs = float(np.clip(rng.normal(43, 17), 0, 95))
            elif hour in range(18, 21):
                carbs = float(np.clip(rng.normal(39, 16), 0, 90))
            else:
                carbs = float(np.clip(rng.normal(3.0, 4.2), 0, 22))
            # Simulated movement is lower overnight and higher in daytime.
            if hour < 6 or hour >= 23:
                steps = int(rng.poisson(35))
            else:
                steps = int(rng.poisson(240 + 70 * np.sin((hour - 6) * np.pi / 14)))
            steps = int(np.clip(steps, 0, 1800))
            circadian = 4.5 * np.sin((hour - 6) * np.pi / 12)
            prev1 = glucose_hist[-1] if glucose_hist else baseline
            prev2 = glucose_hist[-2] if len(glucose_hist) > 1 else baseline
            carb_residual = (0.28 * (patient_wear_rows[-1]["meal_carbs_g_logged"] if patient_wear_rows else 0)
                             + 0.12 * (patient_wear_rows[-2]["meal_carbs_g_logged"] if len(patient_wear_rows) > 1 else 0))
            noise = rng.normal(0, 8.2)
            glucose = (0.64 * prev1 + 0.18 * prev2 + 0.18 * baseline + 0.56 * carbs
                       + carb_residual + circadian - 0.006 * steps - 3.0 * medication_adherence
                       + rng.normal(0, 2.5) + noise)
            glucose = float(np.clip(glucose, 62, 320))
            glucose_hist.append(glucose)
            slope = glucose - prev1
            stress = max(0, 7.0 - sleep_hours) * 2.0 + max(0, 6.0 - medication_adherence * 7) * 1.1
            heart_rate = float(np.clip(68 + 0.32 * (age - 45) + 0.32 * (bmi - 27) + 0.013 * steps + stress + rng.normal(0, 5), 48, 145))
            hrv = float(np.clip(58 - 0.28 * (age - 40) - 0.55 * (bmi - 25) - 0.38 * stress + rng.normal(0, 8), 12, 105))
            patient_wear_rows.append({
                "patient_id": pid, "timestamp": ts.isoformat(sep=" "),
                "current_glucose_mg_dl": round(glucose, 1),
                "glucose_slope_mgdl_hr": round(float(slope), 2),
                "heart_rate_bpm": round(heart_rate, 1), "hrv_ms": round(hrv, 1),
                "steps_last_hour": steps, "sleep_hours_previous_night": round(sleep_hours, 2),
                "meal_carbs_g_logged": round(carbs, 1),
            })
        wearable_rows.extend(patient_wear_rows)
        # The target at time t is the observed synthetic CGM at t+2 hours.
        patient_rows = patient_wear_rows
        for t, row in enumerate(patient_rows[:-2]):
            future_g = patient_rows[t + 2]["current_glucose_mg_dl"]
            label_rows.append({
                "patient_id": pid, "timestamp": row["timestamp"],
                "future_glucose_2h_mg_dl": round(float(future_g), 1),
                "spike_event_2h": int(future_g >= 180.0),
            })

    pd.DataFrame(ehr_rows).to_csv(DATA / "synthetic_ehr.csv", index=False)
    pd.DataFrame(wearable_rows).to_csv(DATA / "synthetic_wearable_hourly.csv", index=False)
    pd.DataFrame(label_rows).to_csv(DATA / "synthetic_labels_2h.csv", index=False)
    print(f"Wrote {len(ehr_rows)} EHR rows, {len(wearable_rows)} wearable rows, {len(label_rows)} outcome labels to {DATA}")

if __name__ == "__main__":
    generate()
