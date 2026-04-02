from __future__ import annotations

import json
import os
from statistics import mean

from app.env import ERTriageEnvironment
from app.models import BaselineRunResult, TaskName
from baselines.rule_based import choose_action


def run_rule_baseline() -> list[BaselineRunResult]:
    env = ERTriageEnvironment()
    results: list[BaselineRunResult] = []
    for task in (TaskName.EASY, TaskName.MEDIUM, TaskName.HARD):
        observation = env.reset(seed=7, task=task)
        scores: list[float] = []
        done = False
        while not done:
            action = choose_action(observation)
            observation = env.step(action)
            scores.append(float(observation.metadata["grader"]["patient_score"]))
            done = observation.done
        results.append(
            BaselineRunResult(
                task=task,
                mean_score=round(mean(scores), 4),
                episode_scores=scores,
                agent_name="heuristic",
            )
        )
    return results


def main() -> None:
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "heuristic"
    if provider != "heuristic":
        print("OPENAI_API_KEY detected. This starter keeps the scored baseline deterministic and uses the heuristic baseline by default.")
    results = run_rule_baseline()
    payload = {
        "provider": provider,
        "results": [result.model_dump() for result in results],
        "average_score": round(mean(result.mean_score for result in results), 4),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
