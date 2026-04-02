from app.graders import grade_patient
from app.models import Action


def test_critical_miss_scores_zero() -> None:
    case = {
        "gold_category": 1,
        "requires_resus": True,
        "bed_required": False,
        "available_beds": 0,
        "waiting_room": 3,
    }
    score, critical_miss, _ = grade_patient(case, Action(triage_category=4, send_to_resus=False, allocate_bed=False))
    assert score == 0.0
    assert critical_miss is True


def test_partial_credit_for_near_miss() -> None:
    case = {
        "gold_category": 3,
        "requires_resus": False,
        "bed_required": False,
        "available_beds": 1,
        "waiting_room": 10,
    }
    score, critical_miss, _ = grade_patient(case, Action(triage_category=4, send_to_resus=False, allocate_bed=False))
    assert 0.0 < score < 1.0
    assert critical_miss is False
