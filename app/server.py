from __future__ import annotations

from fastapi import FastAPI

from app.env import ERTriageEnvironment
from app.models import Action, EpisodeState, ResetRequest, ResetResponse, StepResult

app = FastAPI(title="METAMINDS ER Triage OpenEnv")
ENV = ERTriageEnvironment()
ENV.reset()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/reset", response_model=ResetResponse)
def reset(request: ResetRequest = ResetRequest()) -> ResetResponse:
    observation = ENV.reset(request)
    return ResetResponse(observation=observation)


@app.post("/step", response_model=StepResult)
def step(action: Action) -> StepResult:
    return ENV.step(action)


@app.get("/state", response_model=EpisodeState)
def state() -> EpisodeState:
    return ENV.state()
