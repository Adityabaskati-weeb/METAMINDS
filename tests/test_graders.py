from app.graders import grade_patient
from app.models import Action


def test_critical_miss_scores_zero() -> None:
    case = {
        "gold_category": 1,
        "age_years": 70,
        "arrival_mode": "ambulance",
        "mental_status": "unresponsive",
        "requires_resus": True,
        "bed_required": False,
        "available_beds": 0,
        "waiting_room": 3,
        "queue_by_acuity": [1, 0, 2, 1, 0],
    }
    score, critical_miss, _ = grade_patient(case, Action(triage_category=4, send_to_resus=False, allocate_bed=False))
    assert score == 0.0
    assert critical_miss is True


def test_partial_credit_for_near_miss() -> None:
    case = {
        "gold_category": 3,
        "age_years": 30,
        "arrival_mode": "walk-in",
        "mental_status": "alert",
        "requires_resus": False,
        "bed_required": False,
        "available_beds": 1,
        "waiting_room": 10,
        "queue_by_acuity": [0, 1, 2, 3, 1],
    }
    score, critical_miss, _ = grade_patient(case, Action(triage_category=4, send_to_resus=False, allocate_bed=False))
    assert 0.0 < score < 1.0
    assert critical_miss is False
