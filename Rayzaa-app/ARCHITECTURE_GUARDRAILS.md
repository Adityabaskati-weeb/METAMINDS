# Architecture Guardrails

## Product Truth

- `Rayzaa` is the operational trust intelligence platform.
- `PayEasy + Razorpay Test Mode` is the live source for the demo.
- `Trust Replay` is a forensic reconstruction layer, not a separate scoring engine.

## Backend Truth

- Live API ingest, Razorpay webhook ingest, and scenario replay must continue using the same `_process_event(...)` path.
- Trust-state semantics are locked: `Healthy`, `Watch`, `Fractured`, `Escalated`.
- Typed evidence semantics are locked:
  - `Model Evidence`
  - `Graph Evidence`
  - `Drift Evidence`
  - `Policy Evidence`

## ML Guardrails

- Keep `XGBoost + SHAP + graph heuristics + drift + policy fusion`.
- SHAP belongs only in `Model Evidence`.
- Do not add RL, PPO, GNN-first scoring, or autonomous-agent semantics.

## Replay Guardrails

- Replay must use real inference.
- Replay cases must remain isolated from the live case list and live queue.
- Startup rehydration must ignore replay transactions and replay cases.
- Replay is read-only from the analyst action surface.

## Frontend Guardrails

- Frontend renders backend truth; it does not invent fraud reasoning.
- Queue ordering must remain backend-authored.
- Replay chronology must remain backend-authored.
- Evidence grouping must remain backend-authored.

## Workspace Guardrails

- Builds, validation, replay, and demos run only from `C:\Projects\Rayzaa`.
- Runtime artifacts stay under `.runtime`.
- Do not reintroduce OneDrive-based build or validation flows.
