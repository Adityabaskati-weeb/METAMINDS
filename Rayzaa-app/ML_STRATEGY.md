# ML Strategy Freeze

Rayzaa's MVP ML stack is locked.

## Approved Stack

- `XGBoost` primary scorer
- `SHAP` for model evidence only
- graph heuristics for relationship pressure
- drift scoring for behavioral deviation
- policy fusion for trust-state and queue routing

## Explicitly Out Of Scope

Do not add:

- RL or PPO
- autonomous fraud agents
- GNN-first scoring
- TabTransformer or neural-hype replacements
- frontend-generated evidence

## Verified Operational Truth

- IBM AML is used to train the approved scorer bundle.
- Live API ingest uses real inference.
- Razorpay webhook ingest uses real inference.
- Replay recomputes real inference.
- SHAP values are model-derived and stay inside `Model Evidence`.

## Locked Benchmark

- ROC AUC: `0.94449`
- PR AUC: `0.84365`
- Precision@0.5: `0.72040`
- Recall@0.5: `0.79006`
- F1@0.5: `0.75362`

These metrics are good enough. Do not destabilize the demo chasing marginal gains.

## Artifact Governance

- Approved bundle: `benchmark_v3`
- Approved manifest: [docs/approved_model_artifact.json](./docs/approved_model_artifact.json)
- Demo and dev mode must validate the approved bundle before startup.
- Benchmark mode is the only mode allowed to rebuild the artifact intentionally.
