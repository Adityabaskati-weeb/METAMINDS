from app.env import ERTriageEnvironment
from app.models import Action, ResetRequest, TaskName


def test_easy_task_finishes_in_one_step() -> None:
    env = ERTriageEnvironment()
    env.reset(ResetRequest(task=TaskName.EASY))
    result = env.step(Action(triage_category=1, send_to_resus=True, allocate_bed=True))
    assert result.done is True
    assert result.info.gold_category == 1


def test_hard_task_tracks_progress() -> None:
    env = ERTriageEnvironment()
    observation = env.reset(ResetRequest(task=TaskName.HARD))
    steps = 0
    while True:
        action = Action(triage_category=observation.previous_category or 3, send_to_resus=False, allocate_bed=False)
        result = env.step(action)
        steps += 1
        if result.done:
            break
        observation = result.observation
    assert steps == 5
