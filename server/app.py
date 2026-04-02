from __future__ import annotations

from fastapi.responses import HTMLResponse

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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> str:
    return """
    <html>
      <head><title>METAMINDS ER Triage</title></head>
      <body style="font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; line-height: 1.5;">
        <h1>METAMINDS ER Triage</h1>
        <p>OpenEnv-compatible emergency department triage environment.</p>
        <ul>
          <li><a href="/health">/health</a></li>
          <li><a href="/metadata">/metadata</a></li>
          <li><a href="/schema">/schema</a></li>
          <li><a href="/docs">/docs</a></li>
        </ul>
      </body>
    </html>
    """


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
