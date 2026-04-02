# Deployment Guide

This document follows the OpenEnv deployment flow for a FastAPI-backed environment that can run locally, in Docker, and on Hugging Face Spaces.

## Deployment Files

The deployment entrypoints for this environment are:

- [openenv.yaml](/C:/Users/baska/OneDrive/Documents/New%20project/openenv.yaml)
- [server/app.py](/C:/Users/baska/OneDrive/Documents/New%20project/server/app.py)
- [server/requirements.txt](/C:/Users/baska/OneDrive/Documents/New%20project/server/requirements.txt)
- [Dockerfile](/C:/Users/baska/OneDrive/Documents/New%20project/Dockerfile)
- [server/Dockerfile](/C:/Users/baska/OneDrive/Documents/New%20project/server/Dockerfile)

## Local Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

OpenEnv-style script entrypoint:

```bash
uv run server --host 0.0.0.0 --port 8000
```

## Local Runtime Validation

From the project root:

```bash
openenv validate --json
openenv validate --url http://localhost:8000
```

Expected runtime endpoints:

- `GET /health`
- `GET /metadata`
- `GET /schema`
- `POST /reset`
- `POST /step`
- `GET /state`
- `POST /mcp`

## Docker Build And Run

Build from the project root:

```bash
docker build -t metaminds-er-triage .
```

Run:

```bash
docker run --rm -p 8000:8000 metaminds-er-triage
```

If you want to build from the server-focused Dockerfile explicitly:

```bash
docker build -f server/Dockerfile -t metaminds-er-triage .
```

## Container Smoke Check

After the container starts:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metadata
curl http://localhost:8000/schema
```

Then validate the live server:

```bash
openenv validate --url http://localhost:8000
```

## Hugging Face Spaces

Recommended Space type:

- Docker Space

Recommended steps:

1. Push the repository to GitHub.
2. Create a new Hugging Face Docker Space.
3. Connect the GitHub repository or upload the repo contents.
4. Keep [openenv.yaml](/C:/Users/baska/OneDrive/Documents/New%20project/openenv.yaml) at the repo root.
5. Make sure the app listens on port `8000`.
6. Add the `openenv` tag in the Space metadata.
7. After deployment, run runtime checks on the live URL.

## Hugging Face Post-Deploy Checklist

- Space builds successfully
- `/health` returns `healthy`
- `/metadata` returns environment name and description
- `/schema` returns action, observation, and state schemas
- `/reset`, `/step`, and `/state` work
- `openenv validate --url <space-url>` passes

## Notes

- The root [Dockerfile](/C:/Users/baska/OneDrive/Documents/New%20project/Dockerfile) and [server/Dockerfile](/C:/Users/baska/OneDrive/Documents/New%20project/server/Dockerfile) are intentionally aligned so the environment can be built from the project root or in a tutorial-style server-focused deployment flow.
- Runtime logs and eval outputs can be written under [outputs/logs](/C:/Users/baska/OneDrive/Documents/New%20project/outputs/logs) and [outputs/evals](/C:/Users/baska/OneDrive/Documents/New%20project/outputs/evals).
