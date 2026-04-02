from __future__ import annotations

from app.models import Action, Observation


RED_FLAG_TERMS = ("unresponsive", "collapse", "stroke", "cardiac", "unilateral weakness")
NEURO_TERMS = ("slurred speech", "facial droop", "weakness", "confusion")
AIRWAY_TERMS = ("wheeze", "stridor", "lip swelling", "shortness of breath", "peanut exposure")
SHOCK_TERMS = ("bleeding", "postpartum", "sepsis", "rigors", "diaphoresis")
LOW_ACUITY_TERMS = ("ankle", "sprain", "twisted", "minor")


def choose_action(observation: Observation) -> Action:
    complaint = observation.patient_complaint.lower()
    arrival_mode = observation.arrival_mode.lower()
    mental_status = observation.mental_status.lower()
    vitals = observation.vitals

    category = 5
    if any(term in complaint for term in LOW_ACUITY_TERMS) and vitals.oxygen_saturation >= 98 and vitals.blood_pressure_sys >= 110:
        category = 5
    elif any(term in complaint for term in SHOCK_TERMS) and (vitals.blood_pressure_sys < 90 or vitals.heart_rate > 125):
        category = 1
    elif any(term in complaint for term in RED_FLAG_TERMS) or "collapse" in arrival_mode:
        category = 1
    elif any(term in complaint for term in AIRWAY_TERMS) and vitals.oxygen_saturation <= 90:
        category = 1
    elif any(term in complaint for term in NEURO_TERMS):
        category = 2
    elif vitals.oxygen_saturation < 90 or vitals.blood_pressure_sys < 90:
        category = 2
    elif observation.age_years <= 5 and vitals.temperature_c >= 39.0 and vitals.heart_rate > 140:
        category = 3
    elif "ambulance" in arrival_mode and ("drowsy" in mental_status or "confused" in mental_status):
        category = 2
    elif any(term in complaint for term in AIRWAY_TERMS):
        category = 2
    elif vitals.heart_rate > 120 or vitals.temperature_c >= 39.0:
        category = 2
    elif vitals.heart_rate > 100 or vitals.respiratory_rate > 20 or observation.pain_score >= 8:
        category = 3
    elif observation.waiting_room > 8:
        category = 4

    send_to_resus = category <= 2 and (
        "stroke" in complaint
        or "unresponsive" in complaint
        or "chest pain" in complaint
        or "slurred speech" in complaint
        or "facial droop" in complaint
        or "bleeding" in complaint
        or "lip swelling" in complaint
        or vitals.oxygen_saturation < 90
        or "collapse" in arrival_mode
    )
    allocate_bed = observation.available_beds > 0 and (
        category <= 2
        or ("ambulance" in arrival_mode and category == 3)
        or (observation.age_years <= 5 and category == 3)
    )
    return Action(triage_category=category, send_to_resus=send_to_resus, allocate_bed=allocate_bed)
