from __future__ import annotations

import json
import os
import time
from statistics import mean

from app.env import ERTriageEnvironment
from app.models import BaselineRunResult, TaskName, extract_step_info
from app.tasks import task_episode_count
from baselines.rule_based import choose_action


def run_rule_baseline(seeds: list[int] | None = None) -> dict[str, object]:
    env = ERTriageEnvironment()
    seeds = seeds or [0, 1, 2]
    results: list[BaselineRunResult] = []
    task_summaries: list[dict[str, object]] = []
    started_at = time.perf_counter()
    for task in (TaskName.EASY, TaskName.MEDIUM, TaskName.HARD):
        scores: list[float] = []
        episode_scores: list[float] = []
        step_counts: list[int] = []
        usable_seeds = seeds[: task_episode_count(task)]
        task_started_at = time.perf_counter()

        for seed in usable_seeds:
            observation = env.reset(seed=seed, task=task)
            per_step_scores: list[float] = []
            steps = 0
            done = False
            while not done:
                action = choose_action(observation)
                observation = env.step(action)
                per_step_scores.append(extract_step_info(observation).patient_score)
                steps += 1
                done = observation.done
            scores.extend(per_step_scores)
            episode_scores.append(round(mean(per_step_scores), 4))
            step_counts.append(steps)

        task_elapsed_ms = round((time.perf_counter() - task_started_at) * 1000, 2)
        results.append(
            BaselineRunResult(
                task=task,
                mean_score=round(mean(scores), 4),
                episode_scores=episode_scores,
                agent_name="heuristic",
            )
        )
        task_summaries.append(
            {
                "task": task.value,
                "episodes_evaluated": len(usable_seeds),
                "steps_per_episode": step_counts,
                "elapsed_ms": task_elapsed_ms,
            }
        )
    total_elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    return {
        "results": results,
        "scaling_summary": {
            "seeds": seeds,
            "task_summaries": task_summaries,
            "total_elapsed_ms": total_elapsed_ms,
        },
    }


def main() -> None:
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "heuristic"
    if provider != "heuristic":
        print("OPENAI_API_KEY detected. This starter keeps the scored baseline deterministic and uses the heuristic baseline by default.")
    benchmark = run_rule_baseline()
    results = benchmark["results"]
    payload = {
        "provider": provider,
        "results": [result.model_dump() for result in results],
        "average_score": round(mean(result.mean_score for result in results), 4),
        "scaling_summary": benchmark["scaling_summary"],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
