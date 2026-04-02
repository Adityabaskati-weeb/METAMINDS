from __future__ import annotations

from typing import Dict

from app.models import Action, Observation
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State


class ERTriageEnv(EnvClient[Action, Observation, State]):
    """Typed OpenEnv client for the METAMINDS ER triage environment."""

    def _step_payload(self, action: Action) -> Dict:
        return action.model_dump()

    def _parse_result(self, payload: Dict) -> StepResult[Observation]:
        obs_data = payload.get("observation", {})
        observation = Observation(**obs_data)
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
