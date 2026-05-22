# Rayzaa

Rayzaa is an operational trust intelligence platform for live payment risk review, typed evidence, trust-state progression, queue handling, and replay-backed investigation.

Product hierarchy:

- `Rayzaa` is the intelligence and investigation system.
- `PayEasy + Razorpay Test Mode` is the live demo source.
- `Trust Replay` is a forensic reconstruction layer that reuses the same scorer, evidence, and fusion path.

## Authoritative Workspace

Use only:

- `C:\Projects\Rayzaa`

The OneDrive repo is a source mirror only. Do not run builds, replay validation, benchmark runs, or demo mode from the OneDrive path.

Bootstrap the authoritative workspace from the mirror:

```powershell
.\scripts\bootstrap_authoritative_workspace.ps1 -TargetRoot C:\Projects\Rayzaa
```

See [docs/authoritative-workspace.md](./docs/authoritative-workspace.md) for the full workspace rules.

## Locked MVP ML Stack

- `XGBoost` primary scorer
- `SHAP` for model evidence only
- graph heuristics for shared-device, merchant, ring, and neighbor pressure
- drift scoring for dormant reactivation and geographic/temporal deviation
- policy fusion for trust-state promotion and queue routing

The approved model bundle is `benchmark_v3`. Demo and dev mode now lock to that bundle and do not allow lazy retraining.

See:

- [ML_STRATEGY.md](./ML_STRATEGY.md)
- [docs/approved_model_artifact.json](./docs/approved_model_artifact.json)

## Operational Surfaces

- Signal Rail
- Evidence Lens
- Trust Memory Graph
- Trust Replay
- Case Timeline
- Trust Escalation Queue
- Policy Lab
- Live Payment Proof

## Modes

### Dev

```powershell
.\scripts\start_dev.ps1
```

### Demo

```powershell
.\scripts\start_demo.ps1
```

Demo mode now:

- resets the demo database before startup
- prewarms and validates the locked model artifact
- seeds benign baseline context
- locks replay behind one live payment

### Benchmark

```powershell
.\scripts\run_benchmark.ps1
```

Benchmark mode is the only mode allowed to intentionally rebuild the model artifact.

## Demo Order

The demo order is frozen:

1. Seed benign baseline.
2. Complete one live PayEasy/Razorpay test payment.
3. Show trust-state transition and typed evidence.
4. Show queue update and Telegram alert.
5. Open Trust Replay.

Do not run replay before the live payment in demo mode.

See [DEMO_MODE.md](./DEMO_MODE.md) for the exact command sequence.

## Notes

- Live API ingest, Razorpay webhook ingest, and scenario replay all call the same backend `_process_event(...)` path.
- SHAP stays inside `Model Evidence` only.
- Replay uses real inference, but replay cases are isolated from the live case list, live queue, and startup rehydration.
- `scripts\check_frontend_build.ps1` performs a bounded production build with mode-specific `.next-*` output directories.
- `scripts\reset_caches.ps1` clears runtime state, logs, replay artifacts, and optional databases without polluting the source tree.

## Governance

- [ARCHITECTURE_GUARDRAILS.md](./ARCHITECTURE_GUARDRAILS.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [docs/frontend-visualization-guide.md](./docs/frontend-visualization-guide.md)
