from __future__ import annotations

from app.models import Action


def grade_patient(case: dict, action: Action) -> tuple[float, bool, dict[str, float]]:
    gold = case["gold_category"]
    diff = abs(action.triage_category - gold)
    requires_resus = case.get("requires_resus", False)
    bed_required = case.get("bed_required", False)
    available_beds = case.get("available_beds", 0)

    components = {
        "category_accuracy": 0.0,
        "safety": 0.0,
        "resource_use": 0.0,
        "efficiency": -0.05 if case.get("waiting_room", 0) > 8 else 0.0,
    }

    critical_miss = gold == 1 and action.triage_category > 2
    if critical_miss:
        return 0.0, True, components

    if diff == 0:
        components["category_accuracy"] = 0.7
    elif diff == 1:
        if action.triage_category < gold:
            components["category_accuracy"] = 0.3
        else:
            components["category_accuracy"] = 0.45
    else:
        components["category_accuracy"] = 0.0

    if requires_resus and action.send_to_resus:
        components["safety"] = 0.2
    elif requires_resus and not action.send_to_resus:
        components["safety"] = -0.3
    elif not requires_resus and action.send_to_resus:
        components["safety"] = -0.05
    else:
        components["safety"] = 0.1

    if bed_required:
        if available_beds > 0 and action.allocate_bed:
            components["resource_use"] = 0.15
        elif available_beds == 0 and not action.allocate_bed:
            components["resource_use"] = 0.1
        else:
            components["resource_use"] = -0.1
    elif action.allocate_bed and available_beds == 0:
        components["resource_use"] = -0.05
    else:
        components["resource_use"] = 0.05

    score = max(0.0, min(1.0, round(sum(components.values()), 4)))
    return score, False, components
