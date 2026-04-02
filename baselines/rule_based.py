from __future__ import annotations

from app.models import Action, Observation


RED_FLAG_TERMS = ("unresponsive", "collapse", "stroke", "cardiac", "unilateral weakness")


def choose_action(observation: Observation) -> Action:
    complaint = observation.patient_complaint.lower()
    vitals = observation.vitals

    category = 5
    if any(term in complaint for term in RED_FLAG_TERMS):
        category = 1
    elif vitals.oxygen_saturation < 90 or vitals.blood_pressure_sys < 90:
        category = 2
    elif vitals.heart_rate > 120 or vitals.temperature_c >= 39.0:
        category = 2
    elif vitals.heart_rate > 100 or vitals.respiratory_rate > 20:
        category = 3
    elif observation.waiting_room > 8:
        category = 4

    send_to_resus = category <= 2 and (
        "stroke" in complaint
        or "unresponsive" in complaint
        or "chest pain" in complaint
        or vitals.oxygen_saturation < 90
    )
    allocate_bed = observation.available_beds > 0 and category <= 2
    return Action(triage_category=category, send_to_resus=send_to_resus, allocate_bed=allocate_bed)
