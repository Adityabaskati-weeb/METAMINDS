# Contributing

## Workspace

- Build and run only from `C:\Projects\Rayzaa`.
- Treat the OneDrive repo as a mirror only.
- Keep generated files under `.runtime`.

## ML Governance

Do not reopen the MVP ML stack without an explicit request.

Locked stack:

- `XGBoost`
- `SHAP`
- graph heuristics
- drift scoring
- policy fusion

Do not add:

- RL / PPO
- autonomous agents
- GNN-first scoring
- neural-hype replacements

## Replay Governance

- Do not bypass the shared replay/live scorer path.
- Do not change chronology ordering.
- Do not make replay cases writable from the analyst workflow.
- Do not mix replay evidence into the live case list or startup rehydration.

## Frontend Boundaries

- Keep `command-center.jsx` as the main state owner.
- Do not generate evidence or trust-state logic in the frontend.
- Do not locally rerank the queue.

## Artifact Governance

- The approved bundle is `benchmark_v3`.
- Demo and dev mode must validate the approved artifact manifest before startup.
- Use benchmark mode for intentional artifact rebuilds only.
