from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from app.models import Action, Observation, TaskName, extract_step_info
from client import ERTriageEnv

SYSTEM_PROMPT = """You are an emergency department triage assistant.
Read the patient context and respond with JSON only.
Return:
{
  "triage_category": <integer 1-5>,
  "send_to_resus": <true|false>,
  "allocate_bed": <true|false>
}
Do not include explanations outside JSON.
"""


@dataclass
class EpisodeExample:
    task: TaskName
    seed: int
    prompt: str


def observation_to_prompt(observation: Observation) -> str:
    vitals = observation.vitals
    queue_summary = ", ".join(str(v) for v in observation.queue_by_acuity) or "none"
    return f"""
Task: {observation.task.value}
Patient ID: {observation.patient_id}
Complaint: {observation.patient_complaint}
Age: {observation.age_years}
Arrival mode: {observation.arrival_mode}
Mental status: {observation.mental_status}
Pain score: {observation.pain_score}/10
Vitals:
- Heart rate: {vitals.heart_rate}
- BP: {vitals.blood_pressure_sys}/{vitals.blood_pressure_dia}
- Oxygen saturation: {vitals.oxygen_saturation}
- Respiratory rate: {vitals.respiratory_rate}
- Temperature: {vitals.temperature_c}
Waiting room count: {observation.waiting_room}
Available beds: {observation.available_beds}
Queue by acuity (cat1..cat5): {queue_summary}
Elapsed shift minutes: {observation.elapsed_shift_minutes}
Patients remaining after this one: {observation.patients_remaining}
Clinical notes: {"; ".join(observation.notes) if observation.notes else "none"}
Respond with JSON only.
""".strip()


def extract_json_block(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return match.group(0)


def parse_action_response(text: str) -> Action:
    payload = json.loads(extract_json_block(text))
    return Action(**payload)


def build_training_examples() -> list[EpisodeExample]:
    examples: list[EpisodeExample] = []
    for task in (TaskName.EASY, TaskName.MEDIUM, TaskName.HARD):
        seed_count = 3 if task != TaskName.HARD else 2
        for seed in range(seed_count):
            with ERTriageEnv(base_url=_default_base_url()).sync() as client:
                result = client.reset(seed=seed, task=task.value)
                prompt = observation_to_prompt(result.observation)
            examples.append(EpisodeExample(task=task, seed=seed, prompt=prompt))
    return examples


def rollout_episode(base_url: str, task: TaskName, seed: int, generate_fn: Any) -> dict[str, Any]:
    total_reward = 0.0
    patient_scores: list[float] = []
    transcript: list[dict[str, Any]] = []

    with ERTriageEnv(base_url=base_url).sync() as client:
        result = client.reset(seed=seed, task=task.value)
        observation = result.observation

        while True:
            prompt = observation_to_prompt(observation)
            completion = generate_fn(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            action = parse_action_response(completion)
            result = client.step(action)
            observation = result.observation
            step_info = extract_step_info(observation)
            patient_scores.append(step_info.patient_score)
            total_reward += float(result.reward or 0.0)
            transcript.append(
                {
                    "prompt": prompt,
                    "completion": completion,
                    "action": action.model_dump(),
                    "reward": result.reward,
                    "grader": step_info.model_dump(),
                }
            )
            if result.done:
                break

    return {
        "task": task.value,
        "seed": seed,
        "episode_score": round(sum(patient_scores) / max(1, len(patient_scores)), 4),
        "total_reward": round(total_reward, 4),
        "patient_scores": patient_scores,
        "transcript": transcript,
    }


def reward_from_rollout(rollout: dict[str, Any]) -> float:
    return float(rollout["episode_score"])


def build_grpo_training_config() -> dict[str, Any]:
    return {
        "algorithm": "GRPO",
        "environment_url": _default_base_url(),
        "tasks": [task.value for task in (TaskName.EASY, TaskName.MEDIUM, TaskName.HARD)],
        "seeds": {"single_patient": [0, 1, 2], "resource_aware": [0, 1, 2], "sequential_queue": [0, 1]},
        "response_format": "JSON action object",
        "reward_target": "episode_score from environment grader metadata",
        "trainer_hints": {
            "num_generations": 4,
            "max_prompt_length": 1024,
            "max_completion_length": 128,
        },
    }


def example_trl_grpo_loop() -> str:
    return """
from datasets import Dataset
from trl import GRPOConfig, GRPOTrainer
from training.er_triage_grpo import SYSTEM_PROMPT, build_training_examples

examples = build_training_examples()
dataset = Dataset.from_list([{"prompt": ex.prompt, "task": ex.task.value, "seed": ex.seed} for ex in examples])

training_args = GRPOConfig(
    output_dir="outputs/evals/grpo-er-triage",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=1e-5,
    max_prompt_length=1024,
    max_completion_length=128,
)

trainer = GRPOTrainer(
    model="Qwen/Qwen2.5-0.5B-Instruct",
    args=training_args,
    train_dataset=dataset,
)
trainer.train()
""".strip()


def _default_base_url() -> str:
    return os.getenv("ERT_TRIAGE_BASE_URL", "https://prodigyhuh-metaminds-er-triage.hf.space")
