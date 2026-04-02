from __future__ import annotations

import argparse
import json
import os
from typing import Any

from openai import OpenAI

from app.env import ERTriageEnvironment
from app.models import Action, TaskName


LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("METAMINDS_TASK", TaskName.EASY.value)
BENCHMARK = os.getenv("METAMINDS_BENCHMARK", "metaminds_er_triage")
MAX_STEPS = 8
TEMPERATURE = 0.0

SYSTEM_PROMPT = """You are an ER triage assistant.
Return only compact JSON with keys:
- triage_category: integer from 1 to 5
- send_to_resus: boolean
- allocate_bed: boolean

Safety rules:
- category 1 is most urgent
- category 5 is least urgent
- under-triage is worse than over-triage
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenAI inference for the METAMINDS OpenEnv environment.")
    parser.add_argument("--smoke-run", action="store_true", help="Run a single deterministic episode for validation.")
    return parser.parse_args()


def normalize_task(task_name: str) -> TaskName:
    return TaskName(task_name)


def make_client() -> OpenAI:
    if not API_KEY:
        raise RuntimeError("Missing HF_TOKEN (or API_KEY) for OpenAI client authentication.")
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY, timeout=10.0, max_retries=1)


def build_observation_payload(observation: Any) -> dict[str, Any]:
    return {
        "task": observation.task.value,
        "patient_id": observation.patient_id,
        "patient_complaint": observation.patient_complaint,
        "age_years": observation.age_years,
        "arrival_mode": observation.arrival_mode,
        "mental_status": observation.mental_status,
        "pain_score": observation.pain_score,
        "vitals": observation.vitals.model_dump(),
        "waiting_room": observation.waiting_room,
        "available_beds": observation.available_beds,
        "queue_by_acuity": observation.queue_by_acuity,
        "elapsed_shift_minutes": observation.elapsed_shift_minutes,
        "previous_category": observation.previous_category,
        "patients_remaining": observation.patients_remaining,
        "notes": observation.notes,
    }


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(stripped[start : end + 1])
    raise ValueError("Model response did not contain a JSON object.")


def request_action(client: OpenAI, observation: Any) -> Action:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(build_observation_payload(observation), ensure_ascii=True),
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    return Action.model_validate(extract_json_object(content))


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def format_reward(value: float) -> str:
    return f"{value:.2f}"


def format_action(action: Action) -> str:
    return (
        f"triage(category={action.triage_category},"
        f"resus={format_bool(action.send_to_resus)},"
        f"bed={format_bool(action.allocate_bed)})"
    )


def print_start(task: str) -> None:
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def print_step(step: int, action_str: str, reward: float, done: bool, error: str | None) -> None:
    error_value = error if error is not None else "null"
    print(
        f"[STEP] step={step} action={action_str} reward={format_reward(reward)} "
        f"done={format_bool(done)} error={error_value}",
        flush=True,
    )


def print_end(success: bool, rewards: list[float]) -> None:
    rewards_str = ",".join(format_reward(reward) for reward in rewards)
    print(
        f"[END] success={format_bool(success)} steps={len(rewards)} rewards={rewards_str}",
        flush=True,
    )


def run_episode(task: TaskName, seed: int = 0) -> bool:
    env = ERTriageEnvironment()
    client = make_client()
    rewards: list[float] = []
    success = False

    print_start(task.value)
    try:
        observation = env.reset(seed=seed, task=task)
        for step in range(1, MAX_STEPS + 1):
            action = request_action(client, observation)
            action_str = format_action(action)
            observation = env.step(action)
            reward = float(observation.reward or 0.0)
            rewards.append(reward)
            print_step(step, action_str, reward, observation.done, None)
            if observation.done:
                success = True
                break
        if not success and len(rewards) >= MAX_STEPS:
            print_step(len(rewards), "max_steps()", 0.0, False, "max_steps_exceeded")
    except Exception as exc:
        print_step(len(rewards) + 1, "error()", 0.0, False, str(exc))
    finally:
        print_end(success, rewards)
    return success


def main() -> None:
    args = parse_args()
    _ = LOCAL_IMAGE_NAME
    task = normalize_task(TASK_NAME)
    run_episode(task=task, seed=0 if args.smoke_run else 0)


if __name__ == "__main__":
    main()
