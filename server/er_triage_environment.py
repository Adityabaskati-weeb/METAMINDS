from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata

from app.graders import grade_patient
from app.models import Action, EpisodeState, Observation, ResetRequest, StepInfo, TaskName
from app.reward import build_reward
from app.tasks import load_task_cases


class ERTriageEnvironment(Environment[Action, Observation, EpisodeState]):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self) -> None:
        super().__init__()
        self._task = TaskName.EASY
        self._cases: list[dict] = []
        self._index = 0
        self._score_sum = 0.0
        self._metrics: dict[str, float | int] = {}
        self._episode_id = str(uuid4())
        self._previous_category = 0
        self._done = False
        self._seed = 0

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Observation:
        request = ResetRequest(seed=seed, episode_id=episode_id, **kwargs)
        self._task = request.task
        self._seed = request.seed or 0
        self._cases = load_task_cases(request.task, self._seed)
        self._index = 0
        self._score_sum = 0.0
        self._previous_category = 0
        self._done = False
        self._episode_id = request.episode_id or str(uuid4())
        self._metrics = {
            "correct": 0,
            "partial": 0,
            "wrong": 0,
            "critical_misses": 0,
            "under_triage": 0,
            "over_triage": 0,
        }
        return self._build_observation(self._cases[self._index])

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> Observation:
        if self._done:
            raise RuntimeError("Episode is complete. Call reset() before stepping again.")

        case = self._cases[self._index]
        patient_score, critical_miss, components = grade_patient(case, action)
        reward = build_reward(patient_score, components, critical_miss)

        self._score_sum += patient_score
        self._update_metrics(case, action, patient_score, critical_miss)

        self._previous_category = action.triage_category
        self._index += 1
        self._done = self._index >= len(self._cases)
        next_case = case if self._done else self._cases[self._index]

        observation = self._build_observation(next_case)
        info = StepInfo(
            gold_category=case["gold_category"],
            patient_score=patient_score,
            grader_score=patient_score,
            critical_miss=critical_miss,
            task_completed=self._done,
            episode_metrics=self.state.metrics,
        )
        observation.reward = reward.value
        observation.done = self._done
        observation.metadata.update(
            {
                "reward_components": reward.components,
                "reward_reasoning": reward.reasoning,
                "grader": info.model_dump(),
            }
        )
        return observation

    @property
    def state(self) -> EpisodeState:
        delivered = min(self._index, len(self._cases))
        denominator = max(1, len(self._cases))
        return EpisodeState(
            episode_id=self._episode_id,
            task=self._task,
            step_count=delivered,
            delivered=delivered,
            score_so_far=round(self._score_sum / denominator, 4),
            done=self._done,
            metrics=dict(self._metrics),
        )

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="METAMINDS ER Triage",
            description=(
                "Hospital emergency department triage environment with deterministic "
                "single-patient, resource-aware, and queue-based tasks."
            ),
            version="0.1.0",
            author="METAMINDS",
        )

    def _update_metrics(
        self,
        case: dict,
        action: Action,
        patient_score: float,
        critical_miss: bool,
    ) -> None:
        if action.triage_category > case["gold_category"]:
            self._metrics["under_triage"] += 1
        elif action.triage_category < case["gold_category"]:
            self._metrics["over_triage"] += 1

        if patient_score >= 0.95:
            self._metrics["correct"] += 1
        elif patient_score > 0.0:
            self._metrics["partial"] += 1
        else:
            self._metrics["wrong"] += 1

        if critical_miss:
            self._metrics["critical_misses"] += 1

    def _build_observation(self, case: dict) -> Observation:
        patients_remaining = max(0, len(self._cases) - self._index - (0 if self._done else 1))
        return Observation(
            task=self._task,
            patient_id=case["patient_id"],
            patient_complaint=case["patient_complaint"],
            age_years=case["age_years"],
            arrival_mode=case["arrival_mode"],
            mental_status=case["mental_status"],
            pain_score=case["pain_score"],
            vitals=case["vitals"],
            waiting_room=case["waiting_room"],
            available_beds=case["available_beds"],
            queue_by_acuity=case.get("queue_by_acuity", []),
            elapsed_shift_minutes=case.get("elapsed_shift_minutes", 0),
            previous_category=self._previous_category,
            patients_remaining=patients_remaining,
            notes=case.get("notes", []),
        )
