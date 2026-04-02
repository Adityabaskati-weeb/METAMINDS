from __future__ import annotations

from typing import Optional
from uuid import uuid4

from app.graders import grade_patient
from app.models import Action, EpisodeState, Observation, ResetRequest, StepInfo, StepResult, TaskName
from app.reward import build_reward
from app.tasks import load_task_cases


class ERTriageEnvironment:
    def __init__(self) -> None:
        self._task = TaskName.EASY
        self._cases: list[dict] = []
        self._index = 0
        self._score_sum = 0.0
        self._metrics: dict[str, float | int] = {}
        self._episode_id = str(uuid4())
        self._previous_category = 0
        self._done = False

    def reset(self, request: Optional[ResetRequest] = None) -> Observation:
        request = request or ResetRequest()
        self._task = request.task
        self._cases = load_task_cases(request.task)
        self._index = 0
        self._score_sum = 0.0
        self._previous_category = 0
        self._done = False
        self._episode_id = str(uuid4())
        self._metrics = {
            "correct": 0,
            "partial": 0,
            "wrong": 0,
            "critical_misses": 0,
        }
        return self._build_observation(self._cases[self._index])

    def step(self, action: Action) -> StepResult:
        if self._done:
            raise RuntimeError("Episode is complete. Call reset() before stepping again.")

        case = self._cases[self._index]
        patient_score, critical_miss, components = grade_patient(case, action)
        reward = build_reward(patient_score, components, critical_miss)

        self._score_sum += patient_score
        if patient_score >= 0.95:
            self._metrics["correct"] += 1
        elif patient_score > 0.0:
            self._metrics["partial"] += 1
        else:
            self._metrics["wrong"] += 1

        if critical_miss:
            self._metrics["critical_misses"] += 1

        self._previous_category = action.triage_category
        self._index += 1
        self._done = self._index >= len(self._cases)

        if self._done:
            next_case = case
        else:
            next_case = self._cases[self._index]

        observation = self._build_observation(next_case)
        info = StepInfo(
            gold_category=case["gold_category"],
            patient_score=patient_score,
            grader_score=patient_score,
            critical_miss=critical_miss,
            task_completed=self._done,
            episode_metrics=self.state().metrics,
        )
        return StepResult(observation=observation, reward=reward, done=self._done, info=info)

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

    def _build_observation(self, case: dict) -> Observation:
        patients_remaining = max(0, len(self._cases) - self._index - (0 if self._done else 1))
        return Observation(
            task=self._task,
            patient_id=case["patient_id"],
            patient_complaint=case["patient_complaint"],
            vitals=case["vitals"],
            waiting_room=case["waiting_room"],
            available_beds=case["available_beds"],
            previous_category=self._previous_category,
            patients_remaining=patients_remaining,
            notes=case.get("notes", []),
        )
