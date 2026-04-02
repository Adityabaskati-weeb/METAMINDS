import pytest

from app.env import ERTriageEnvironment
from app.models import Action, TaskName


def test_easy_task_finishes_in_one_step() -> None:
    env = ERTriageEnvironment()
    env.reset(task=TaskName.EASY, seed=0)
    observation = env.step(Action(triage_category=1, send_to_resus=True, allocate_bed=True))
    assert observation.done is True
    assert observation.metadata["grader"]["gold_category"] == 1


def test_hard_task_tracks_progress() -> None:
    env = ERTriageEnvironment()
    observation = env.reset(task=TaskName.HARD, seed=0)
    steps = 0
    while True:
        action = Action(triage_category=observation.previous_category or 3, send_to_resus=False, allocate_bed=False)
        observation = env.step(action)
        steps += 1
        if observation.done:
            break
    assert steps == 6


def test_step_after_done_raises() -> None:
    env = ERTriageEnvironment()
    env.reset(task=TaskName.EASY, seed=0)
    env.step(Action(triage_category=1, send_to_resus=True, allocate_bed=True))
    with pytest.raises(RuntimeError):
        env.step(Action(triage_category=1, send_to_resus=True, allocate_bed=True))


def test_reset_is_deterministic_for_same_seed() -> None:
    env = ERTriageEnvironment()
    first = env.reset(task=TaskName.HARD, seed=1)
    second = env.reset(task=TaskName.HARD, seed=1)
    assert first.patient_id == second.patient_id
    assert first.patient_complaint == second.patient_complaint
