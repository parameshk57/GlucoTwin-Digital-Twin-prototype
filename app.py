from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))
from twin_model import FEATURES, load_fused_data, train_and_evaluate

st.set_page_config(page_title="GlucoTwin | Digital Twin PoC", page_icon="🧬", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.35rem; padding-bottom: 2.2rem; max-width: 1500px;}
  .hero {padding: 1.2rem 1.4rem; border-radius: 18px; background: linear-gradient(110deg,#171c3a 0%,#373779 58%,#5f63a8 100%); color: white; margin-bottom: 1rem;}
  .hero h1 {font-size: 2.2rem; margin: 0 0 .25rem 0; letter-spacing: -.03em;}
  .hero p {margin: 0; color: #e4e7ff; font-size: 1rem;}
  .notice {padding: .8rem 1rem; background: #fff7df; border: 1px solid #f4d27e; border-radius: 10px; color: #5b470e; margin: .5rem 0 1rem 0;}
  .section-title {font-size: 1.12rem; font-weight: 700; color: #222748; margin: .2rem 0 .7rem 0;}
  div[data-testid="stMetric"] {background: #f7f8fc; border: 1px solid #e5e8f1; border-radius: 12px; padding: 10px 13px;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Loading synthetic streams and training the model...")
def get_assets():
    model, metrics, fused = train_and_evaluate()
    ehr = pd.read_csv(ROOT / "data" / "synthetic_ehr.csv")
    wearable = pd.read_csv(ROOT / "data" / "synthetic_wearable_hourly.csv", parse_dates=["timestamp"])
    wearable = wearable.merge(ehr, on="patient_id", how="left", validate="many_to_one")
    wearable["hour_of_day"] = wearable["timestamp"].dt.hour.astype(int)
    return model, metrics, fused, ehr, wearable

model, metrics, fused, ehr, wearable = get_assets()

st.markdown("""
<div class="hero">
  <h1>🧬 GlucoTwin</h1>
  <p>Virtual patient prototype · EHR + wearable fusion · 2-hour glucose-spike forecast</p>
</div>
<div class="notice"><b>Research prototype only.</b> All records are synthetic. This model is not a medical device and must not be used for diagnosis, treatment, medication changes, or emergency decisions. The displayed performance is measured only on a synthetic holdout cohort.</div>
""", unsafe_allow_html=True)

# Sidebar selects a synthetic patient/timepoint and provides what-if controls.
st.sidebar.header("Virtual patient controls")
patient_ids = sorted(ehr["patient_id"].unique())
def_patient_idx = patient_ids.index("GT-0007") if "GT-0007" in patient_ids else 0
patient_id = st.sidebar.selectbox("Synthetic patient", patient_ids, index=def_patient_idx)
patient_series = wearable[wearable["patient_id"] == patient_id].sort_values("timestamp").reset_index(drop=True)
obs_idx = st.sidebar.slider("Replay hour", min_value=0, max_value=len(patient_series)-1,
                            value=min(120, len(patient_series)-1), step=1,
                            help="Move through the 7-day simulated sensor stream.")
row = patient_series.iloc[obs_idx]

st.sidebar.divider()
st.sidebar.subheader("What-if sensor update")
st.sidebar.caption("Change current observations to explore how the model responds. This is a simulated scenario, not a treatment recommendation.")
current_glucose = st.sidebar.slider("Current glucose (mg/dL)", 60, 320, int(round(row["current_glucose_mg_dl"])), key=f"glucose_{patient_id}_{obs_idx}")
meal_carbs = st.sidebar.slider("Logged meal carbohydrates (g)", 0, 100, int(round(row["meal_carbs_g_logged"])), key=f"carbs_{patient_id}_{obs_idx}")
steps = st.sidebar.slider("Steps in last hour", 0, 1800, int(row["steps_last_hour"]), step=25, key=f"steps_{patient_id}_{obs_idx}")
sleep = st.sidebar.slider("Previous-night sleep (hours)", 3.0, 10.0, float(row["sleep_hours_previous_night"]), step=0.5, key=f"sleep_{patient_id}_{obs_idx}")
threshold = st.sidebar.slider("Exploratory alert threshold", 0.10, 0.90, 0.50, step=0.05, help="A demo threshold only; not clinically calibrated.")

# Build model input from static EHR fields + the selected dynamic sensor window.
feature_row = row[FEATURES].copy()
base_input = pd.DataFrame([{c: feature_row[c] for c in FEATURES}], columns=FEATURES)
scenario_input = base_input.copy()
scenario_input.loc[0, "current_glucose_mg_dl"] = current_glucose
scenario_input.loc[0, "meal_carbs_g_logged"] = meal_carbs
scenario_input.loc[0, "steps_last_hour"] = steps
scenario_input.loc[0, "sleep_hours_previous_night"] = sleep
base_prob = float(model.predict_proba(base_input)[:, 1][0])
scenario_prob = float(model.predict_proba(scenario_input)[:, 1][0])

# Header with selected synthetic patient context.
st.markdown(f"### Patient twin: `{patient_id}`")
col_profile, col_snapshot = st.columns([1.1, 2.2], gap="large")
with col_profile:
    st.markdown('<div class="section-title">Historical EHR profile</div>', unsafe_allow_html=True)
    st.write(f"**Age:** {int(row['age_years'])} years · **Sex:** {row['sex']}")
    st.write(f"**BMI:** {row['bmi_kg_m2']:.1f} kg/m²")
    st.write(f"**Diabetes duration:** {int(row['diabetes_duration_years'])} years")
    st.write(f"**HbA1c:** {row['hba1c_percent']:.1f}%")
    st.write(f"**Hypertension history:** {'Yes' if row['hypertension_flag'] else 'No'}")
    st.write(f"**Metformin recorded:** {'Yes' if row['metformin_flag'] else 'No'}")
    st.write(f"**Medication adherence (simulated):** {row['medication_adherence_0_1']:.0%}")
with col_snapshot:
    st.markdown('<div class="section-title">Current synthetic wearable snapshot</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Glucose", f"{current_glucose} mg/dL", f"{row['glucose_slope_mgdl_hr']:+.1f} mg/dL/hr slope")
    c2.metric("Heart rate", f"{row['heart_rate_bpm']:.0f} bpm")
    c3.metric("HRV", f"{row['hrv_ms']:.0f} ms")
    c4.metric("Steps last hour", f"{steps:,}")
    st.caption(f"Replay timestamp: {row['timestamp']:%d %b %Y, %H:%M} · Prior-night sleep: {sleep:.1f} h · Logged carbs: {meal_carbs} g")

st.markdown("---")
st.markdown('<div class="section-title">2-hour forecast scenario</div>', unsafe_allow_html=True)
risk_cols = st.columns([1, 1, 1, 1.35])
risk_cols[0].metric("Original-window probability", f"{base_prob:.1%}", "Model output")
risk_cols[1].metric("What-if probability", f"{scenario_prob:.1%}", f"{scenario_prob-base_prob:+.1%} vs. original")
risk_cols[2].metric("Alert threshold", f"{threshold:.0%}", "Exploratory only")
if scenario_prob >= threshold:
    status = "Elevated model signal"
    advice = "Review the surrounding data in context. This is not a diagnosis or a care recommendation."
else:
    status = "Below demo threshold"
    advice = "A lower model score does not rule out risk or replace clinical assessment."
with risk_cols[3]:
    if scenario_prob >= threshold:
        st.warning(status)
    else:
        st.info(status)
    st.caption(advice)

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown('<div class="section-title">Wearable trajectory · preceding 24 hours</div>', unsafe_allow_html=True)
    history = patient_series.iloc[max(0, obs_idx-23):obs_idx+1].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["timestamp"], y=history["current_glucose_mg_dl"], mode="lines+markers", name="Synthetic CGM", line=dict(width=3, color="#5145a8"), marker=dict(size=4)))
    fig.add_hline(y=180, line_dash="dash", line_color="#c85a54", annotation_text="180 mg/dL reference", annotation_position="top left")
    fig.update_layout(height=330, margin=dict(l=5, r=5, t=10, b=5), xaxis_title=None, yaxis_title="Glucose (mg/dL)", legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="white", paper_bgcolor="white")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#edf0f7")
    st.plotly_chart(fig, use_container_width=True)
    activity_fig = px.bar(history, x="timestamp", y="steps_last_hour", title="Activity windows", labels={"timestamp":"Time", "steps_last_hour":"Steps in last hour"})
    activity_fig.update_layout(height=220, margin=dict(l=5, r=5, t=45, b=5), showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    activity_fig.update_xaxes(showgrid=False)
    activity_fig.update_yaxes(gridcolor="#edf0f7")
    st.plotly_chart(activity_fig, use_container_width=True)
with right:
    st.markdown('<div class="section-title">Model evaluation · synthetic holdout</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
    m2.metric("PR-AUC / Avg precision", f"{metrics['average_precision']:.3f}")
    m3, m4 = st.columns(2)
    m3.metric("Recall @ 0.50", f"{metrics['recall_at_0_5']:.3f}")
    m4.metric("Precision @ 0.50", f"{metrics['precision_at_0_5']:.3f}")
    st.caption(f"{metrics['n_train_patients']} train patients / {metrics['n_test_patients']} unseen test patients; {metrics['n_test_rows']:,} test windows. Test event prevalence: {metrics['test_event_prevalence']:.1%}.")
    top_features = pd.DataFrame({"Feature": list(metrics["feature_importance"].keys()), "Importance": list(metrics["feature_importance"].values())}).head(8).sort_values("Importance")
    fi = px.bar(top_features, x="Importance", y="Feature", orientation="h", title="Random Forest feature importance", labels={"Importance":"Relative impurity importance"})
    fi.update_layout(height=365, margin=dict(l=5, r=5, t=45, b=5), showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    fi.update_xaxes(showgrid=False)
    st.plotly_chart(fi, use_container_width=True)

with st.expander("How this prototype works / important limitations"):
    st.markdown("""
    **Fusion:** static synthetic EHR fields (age, BMI, diabetes duration, HbA1c, comorbidity and medication/adherence flags) are joined to hourly synthetic wearable/CGM windows (glucose, glucose slope, heart rate, HRV, activity, sleep and logged carbohydrates).

    **Target:** whether the synthetic glucose value two hours after a time window is at least 180 mg/dL. This is a demonstration target, not a claim that any threshold alone defines a clinical event.

    **Model:** Random Forest classifier. Evaluation uses a patient-level split, so the test patients are not seen during fitting. The threshold shown in the sidebar is exploratory and has not been optimized for real clinical utility.

    **Limitations:** the data-generating process is artificial; its regularities can make synthetic holdout performance look excellent. No prospective study, calibration study, subgroup validation, clinical review or external-dataset validation has been performed. Feature importance is not causal explanation.
    """)

st.markdown("---")
st.caption("GlucoTwin · Digital Twin Challenge proof of concept · Synthetic data only · Built for demonstration, not clinical use")
