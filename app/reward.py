from __future__ import annotations

from app.models import Reward


def build_reward(patient_score: float, components: dict[str, float], critical_miss: bool) -> Reward:
    if critical_miss:
        return Reward(
            value=0.0,
            components=components,
            reasoning="Critical under-triage detected; reward forced to zero for safety.",
        )

    reasoning = "Partial-credit reward combines category accuracy, safety handling, resource use, and queue pressure."
    return Reward(value=patient_score, components=components, reasoning=reasoning)
