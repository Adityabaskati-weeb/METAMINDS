# Training Guide

This project now includes a training scaffold aligned to the OpenEnv training tutorial style: prompt construction, action parsing, environment rollouts, reward extraction, and a GRPO-style training configuration for an LLM policy.

## Training Entry Point

Main helper module:

- [training/er_triage_grpo.py](/C:/Users/baska/OneDrive/Documents/New%20project/training/er_triage_grpo.py)

It provides:

- prompt generation from environment observations
- JSON action parsing
- rollout execution against the deployed environment
- reward extraction from grader metadata
- a GRPO-style training config scaffold
- an example TRL training loop snippet

## Training Flow

The training flow mirrors the OpenEnv tutorial pattern:

1. Reset the environment for a deterministic task/seed.
2. Convert the first observation into a language-model prompt.
3. Ask the model to emit a JSON action.
4. Parse the JSON into the typed OpenEnv `Action`.
5. Step the environment and read grader metadata from the returned observation.
6. Use the episode score as the training reward target.

## Default Environment URL

By default the training scaffold targets the deployed Space:

- [prodigyhuh-metaminds-er-triage.hf.space](https://prodigyhuh-metaminds-er-triage.hf.space)

Override with:

```bash
ERT_TRIAGE_BASE_URL=http://localhost:8000
```

## Example Usage

Build training examples:

```python
from training.er_triage_grpo import build_training_examples

examples = build_training_examples()
print(len(examples))
print(examples[0].prompt)
```

Run a single rollout with your own generation function:

```python
from training.er_triage_grpo import rollout_episode
from app.models import TaskName

def fake_generate(messages):
    return '{"triage_category": 2, "send_to_resus": true, "allocate_bed": false}'

rollout = rollout_episode(
    base_url="https://prodigyhuh-metaminds-er-triage.hf.space",
    task=TaskName.MEDIUM,
    seed=0,
    generate_fn=fake_generate,
)
print(rollout["episode_score"])
```

## GRPO Training Scaffold

The repo includes a tutorial-style GRPO config helper:

```python
from training.er_triage_grpo import build_grpo_training_config

config = build_grpo_training_config()
print(config)
```

The function `example_trl_grpo_loop()` returns a reference snippet showing how to wire the generated prompts into a `trl.GRPOTrainer`.

## Important Note

This repo now includes a **completed lightweight training pipeline** that runs locally and produces:

- generated model path: `outputs/models/er_triage_policy.joblib`
- [outputs/evals/training_report.json](/C:/Users/baska/OneDrive/Documents/New%20project/outputs/evals/training_report.json)

The local trainer is implemented in [training/supervised_policy.py](/C:/Users/baska/OneDrive/Documents/New%20project/training/supervised_policy.py) and serves as the executable training artifact path for this repo.

Current trained-policy evaluation artifact:

- generated model path: `outputs/models/er_triage_policy.joblib`
- training report: [outputs/evals/training_report.json](/C:/Users/baska/OneDrive/Documents/New%20project/outputs/evals/training_report.json)
- trained policy evaluation now uses held-out episode groups rather than the full in-family pool

The binary model file is kept local and is not committed, which keeps GitHub and Hugging Face Space pushes clean.

Current held-out results:

- held-out exact action accuracy: `0.25`
- held-out triage accuracy: `0.50`
- held-out environment evaluation average: `0.545`

Held-out per-task environment evaluation:

- `single_patient`: `0.89`
- `resource_aware`: `0.05`
- `sequential_queue`: `0.695`

Interpretation:

- the earlier near-perfect trained score was too optimistic for such a small dataset
- the held-out results are more honest and show that the training pipeline works, but the model still needs more medium-difficulty data to generalize well

The GRPO scaffold is still useful as the tutorial-aligned next step, but that part still depends on:

- installing training dependencies such as `trl`, `transformers`, and `datasets`
- choosing a model checkpoint
- selecting available compute
- running the trainer for actual optimization

So the project is now:

- fully trained in the lightweight local supervised-policy sense
- scaffolded for the heavier GRPO/TRL tutorial path
