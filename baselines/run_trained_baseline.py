from __future__ import annotations

import json
from statistics import mean

from app.env import ERTriageEnvironment
from app.models import BaselineRunResult, TaskName, extract_step_info
from baselines.trained_policy import choose_trained_action
from training.supervised_policy import default_eval_groups


TASK_SEED_MAP = {
    TaskName.EASY: [2],
    TaskName.MEDIUM: [2],
    TaskName.HARD: [1],
}


def run_trained_baseline() -> dict[str, object]:
    env = ERTriageEnvironment()
    results: list[BaselineRunResult] = []
    for task in (TaskName.EASY, TaskName.MEDIUM, TaskName.HARD):
        scores: list[float] = []
        episode_scores: list[float] = []
        usable_seeds = TASK_SEED_MAP[task]
        for seed in usable_seeds:
            observation = env.reset(seed=seed, task=task)
            per_step_scores: list[float] = []
            done = False
            while not done:
                action = choose_trained_action(observation)
                observation = env.step(action)
                per_step_scores.append(extract_step_info(observation).patient_score)
                done = observation.done
            scores.extend(per_step_scores)
            episode_scores.append(round(mean(per_step_scores), 4))
        results.append(
            BaselineRunResult(
                task=task,
                mean_score=round(mean(scores), 4),
                episode_scores=episode_scores,
                agent_name="trained",
            )
        )
    payload = {
        "results": [result.model_dump() for result in results],
        "average_score": round(mean(result.mean_score for result in results), 4),
        "artifact_path": "outputs/models/er_triage_policy.joblib",
        "eval_groups": default_eval_groups(),
    }
    return payload


def main() -> None:
    print(json.dumps(run_trained_baseline(), indent=2))


if __name__ == "__main__":
    main()
