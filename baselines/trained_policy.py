from __future__ import annotations

from app.models import Action, Observation
from training.supervised_policy import predict_action


def choose_trained_action(observation: Observation) -> Action:
    return predict_action(observation)
