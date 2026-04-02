---
title: METAMINDS ER Triage
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: docker
app_port: 8000
---

# METAMINDS: Hospital ER Triage OpenEnv Environment

METAMINDS is a real-world OpenEnv environment that simulates hospital emergency-room triage. An agent observes incoming patients, assigns an urgency category, and decides whether to escalate or allocate scarce resources. The environment is designed for hackathon judging: deterministic tasks, shaped rewards, typed models, reproducible baseline scoring, Docker support, and deployment readiness for Hugging Face Spaces.

## Why This Environment

ER triage is a realistic workflow carried out by nurses and emergency clinicians every day. It is safety-critical, resource-constrained, and naturally supports partial-credit evaluation. That makes it a good fit for OpenEnv: the agent must reason about patient severity, queue pressure, and limited beds instead of solving a toy problem.

## Environment API

The environment exposes the standard OpenEnv-style API:

- `POST /reset` returns the initial observation for a selected task.
- `POST /step` accepts an action and returns `observation`, `reward`, `done`, and `info`.
- `GET /state` returns the current environment state.
- `GET /health` is a simple health check.
- `GET /metadata` returns environment metadata.
- `GET /schema` returns action, observation, and state schemas.

Core implementation lives in [server/app.py](/C:/Users/baska/OneDrive/Documents/New%20project/server/app.py), [server/er_triage_environment.py](/C:/Users/baska/OneDrive/Documents/New%20project/server/er_triage_environment.py), [app/models.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/models.py), and [client.py](/C:/Users/baska/OneDrive/Documents/New%20project/client.py).

## Project Layout

This repository now follows the OpenEnv environment scaffold more closely:

- [__init__.py](/C:/Users/baska/OneDrive/Documents/New%20project/__init__.py) exports the public package API
- [client.py](/C:/Users/baska/OneDrive/Documents/New%20project/client.py) provides a typed `EnvClient`
- [app/models.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/models.py) defines action, observation, reward, and state models
- [server/er_triage_environment.py](/C:/Users/baska/OneDrive/Documents/New%20project/server/er_triage_environment.py) implements the environment logic
- [server/app.py](/C:/Users/baska/OneDrive/Documents/New%20project/server/app.py) exposes the FastAPI/OpenEnv server
- [server/requirements.txt](/C:/Users/baska/OneDrive/Documents/New%20project/server/requirements.txt) contains container runtime dependencies
- [openenv.yaml](/C:/Users/baska/OneDrive/Documents/New%20project/openenv.yaml) declares the environment manifest
- [outputs](/C:/Users/baska/OneDrive/Documents/New%20project/outputs) stores runtime logs and evaluation artifacts

## Action Space

`Action` is a typed Pydantic model with:

- `triage_category: int` in `1..5`
- `send_to_resus: bool`
- `allocate_bed: bool`

Example:

```json
{
  "triage_category": 2,
  "send_to_resus": true,
  "allocate_bed": false
}
```

## Observation Space

`Observation` includes:

- `task`
- `patient_id`
- `patient_complaint`
- `age_years`
- `arrival_mode`
- `mental_status`
- `pain_score`
- `vitals`
- `waiting_room`
- `available_beds`
- `queue_by_acuity`
- `elapsed_shift_minutes`
- `previous_category`
- `patients_remaining`
- `notes`

Vitals include heart rate, blood pressure, oxygen saturation, respiratory rate, and temperature.

## State Space

`EpisodeState` tracks:

- `episode_id`
- `task`
- `step_count`
- `delivered`
- `score_so_far`
- `done`
- `metrics`

## Tasks

### 1. Easy: Single Patient

One patient, one triage decision. These scenarios focus on clean triage categorization for clearly recognizable presentations such as acute coronary syndrome, stroke-alert symptoms, and low-acuity orthopedic injury.

### 2. Medium: Resource Aware

Adds queue pressure, bed constraints, pediatric cases, and ambulance arrivals. The agent must still triage correctly, but also behave safely when monitored beds are scarce or the waiting room is overloaded.

### 3. Hard: Sequential Queue

A six-patient episode with changing acuity, evolving queue pressure, and repeated competition for monitored care. The final score reflects consistent decision quality across a realistic shift slice instead of a single isolated case.

## Reward Design

The reward is shaped across the trajectory rather than only at the end:

- exact triage match earns the largest share of reward
- near misses receive partial credit
- correct escalation and sensible bed usage improve reward
- queue pressure adds a small efficiency penalty
- critical under-triage forces the patient score to `0.0`

Grading logic is implemented in [app/graders.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/graders.py) and [app/reward.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/reward.py).

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

You can also run the environment through the OpenEnv-style script entrypoint:

```bash
uv run server --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker build -t metaminds-er-triage .
docker run -p 8000:8000 metaminds-er-triage
```

Detailed deployment instructions live in [deployment.md](/C:/Users/baska/OneDrive/Documents/New%20project/deployment.md).

## Baseline Inference

The starter baseline is deterministic and heuristic-based so scores are reproducible. It also checks for `OPENAI_API_KEY` so the repo is ready for an API-driven agent extension later.

Run:

```bash
python baselines/run_baseline.py
```

Expected starter baseline scores after the first scaffold pass:

- easy: `1.00`
- medium: `0.62`
- hard: `0.8233`
- average: `0.8144`

Replace the heuristic in [baselines/rule_based.py](/C:/Users/baska/OneDrive/Documents/New%20project/baselines/rule_based.py) with an OpenAI-driven policy for your final submission baseline script if you want the model to act directly.

## Client Usage

The repo includes a typed OpenEnv client in [client.py](/C:/Users/baska/OneDrive/Documents/New%20project/client.py).

Example:

```python
from app.models import Action
from client import ERTriageEnv

with ERTriageEnv(base_url="http://localhost:8000").sync() as client:
    result = client.reset()
    result = client.step(Action(triage_category=2, send_to_resus=True, allocate_bed=False))
    print(result.reward, result.done)
```

## Testing

```bash
pytest
```

Tests cover:

- model validation
- grader behavior
- task progression
- API smoke checks

## Hugging Face Spaces

This repo is set up to be containerized and deployed as a Docker-based Hugging Face Space. For submission:

1. Push this repository to GitHub.
2. Create a new Docker Space on Hugging Face.
3. Import the repo or mirror these files into the Space.
4. Tag the Space with `openenv`.
5. Verify `/health`, `/metadata`, `/schema`, `/reset`, `/step`, and `/state`.

Live deployment:

- Space: [prodigyhuh/metaminds-er-triage](https://huggingface.co/spaces/prodigyhuh/metaminds-er-triage)
- Direct runtime URL: [prodigyhuh-metaminds-er-triage.hf.space](https://prodigyhuh-metaminds-er-triage.hf.space)

Live runtime validation:

```bash
openenv validate --url https://prodigyhuh-metaminds-er-triage.hf.space
```

Result:

- passed all 6 required runtime criteria

## Suggested Next Improvements

- add `openenv validate` in CI once the `openenv` package version is pinned
- expand the synthetic patient bank from 7 curated cases to 50-100 deterministic cases
- add a true OpenAI baseline agent that calls the API and logs reproducible per-task scores
- add episode transcripts for demo day
