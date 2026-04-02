from __future__ import annotations

from app.models import Action, Observation
from openenv.core.env_server.http_server import create_app
from server.er_triage_environment import ERTriageEnvironment

app = create_app(
    ERTriageEnvironment,
    Action,
    Observation,
    env_name="metaminds_er_triage",
    max_concurrent_envs=4,
)


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
