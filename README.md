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

Core implementation lives in [app/server.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/server.py), [app/env.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/env.py), and [app/models.py](/C:/Users/baska/OneDrive/Documents/New%20project/app/models.py).

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
- `vitals`
- `waiting_room`
- `available_beds`
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

One patient, one triage decision. This validates core classification and critical escalation.

### 2. Medium: Resource Aware

Adds queue pressure and bed constraints. The agent still triages correctly, but must also behave safely when resources are unavailable.

### 3. Hard: Sequential Queue

A five-patient episode with changing acuity and limited capacity. The final score reflects consistency over the whole sequence.

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
uvicorn app.server:app --host 0.0.0.0 --port 7860
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 7860
```

## Docker

```bash
docker build -t metaminds-er-triage .
docker run -p 7860:7860 metaminds-er-triage
```

## Baseline Inference

The starter baseline is deterministic and heuristic-based so scores are reproducible. It also checks for `OPENAI_API_KEY` so the repo is ready for an API-driven agent extension later.

Run:

```bash
python baselines/run_baseline.py
```

Expected starter baseline scores after the first scaffold pass:

- easy: around `0.95-1.00`
- medium: around `0.70-0.90`
- hard: around `0.55-0.80`

Replace the heuristic in [baselines/rule_based.py](/C:/Users/baska/OneDrive/Documents/New%20project/baselines/rule_based.py) with an OpenAI-driven policy for your final submission baseline script if you want the model to act directly.

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
5. Verify `/health`, `/reset`, `/step`, and `/state`.

## Suggested Next Improvements

- add `openenv validate` in CI once the `openenv` package version is pinned
- expand the synthetic patient bank from 7 curated cases to 50-100 deterministic cases
- add a true OpenAI baseline agent that calls the API and logs reproducible per-task scores
- add episode transcripts for demo day
