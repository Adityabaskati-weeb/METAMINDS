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
      <head>
        <title>METAMINDS ER Triage</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          :root {
            --bg: #f7f3ec;
            --surface: rgba(255, 255, 255, 0.78);
            --surface-strong: rgba(255, 255, 255, 0.92);
            --text: #161616;
            --muted: #5f5b57;
            --line: rgba(22, 22, 22, 0.12);
            --accent: #b23a2f;
            --accent-soft: #f4d7d3;
            --ink: #1d3c45;
            --shadow: 0 20px 60px rgba(26, 18, 11, 0.10);
          }

          * { box-sizing: border-box; }

          body {
            margin: 0;
            font-family: "Segoe UI", "Aptos", sans-serif;
            color: var(--text);
            background:
              radial-gradient(circle at top left, rgba(178, 58, 47, 0.18), transparent 32%),
              radial-gradient(circle at bottom right, rgba(29, 60, 69, 0.16), transparent 30%),
              linear-gradient(180deg, #fbf7f1 0%, var(--bg) 100%);
          }

          .shell {
            max-width: 1080px;
            margin: 0 auto;
            padding: 40px 20px 56px;
          }

          .hero {
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.72));
            border: 1px solid var(--line);
            border-radius: 28px;
            box-shadow: var(--shadow);
            padding: 34px;
            overflow: hidden;
            position: relative;
          }

          .hero::after {
            content: "";
            position: absolute;
            right: -80px;
            top: -80px;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(178, 58, 47, 0.22), transparent 65%);
          }

          .eyebrow {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 14px;
          }

          h1 {
            margin: 0 0 12px;
            font-size: clamp(36px, 5vw, 58px);
            line-height: 0.98;
            letter-spacing: -0.04em;
          }

          .lede {
            max-width: 720px;
            margin: 0;
            color: var(--muted);
            font-size: 18px;
            line-height: 1.65;
          }

          .hero-grid,
          .task-grid,
          .endpoint-grid {
            display: grid;
            gap: 16px;
            margin-top: 26px;
          }

          .hero-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
          .task-grid { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
          .endpoint-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

          .stat,
          .card,
          .endpoint {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px;
            backdrop-filter: blur(10px);
          }

          .stat strong {
            display: block;
            font-size: 28px;
            margin-bottom: 4px;
          }

          .stat span,
          .card p,
          .endpoint p,
          .footer-note {
            color: var(--muted);
          }

          .section {
            margin-top: 28px;
          }

          .section h2 {
            margin: 0 0 14px;
            font-size: 22px;
            letter-spacing: -0.03em;
          }

          .card h3,
          .endpoint h3 {
            margin: 0 0 8px;
            font-size: 18px;
          }

          .pill {
            display: inline-block;
            margin-top: 10px;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(29, 60, 69, 0.09);
            color: var(--ink);
            font-size: 12px;
            font-weight: 700;
          }

          .endpoint a {
            color: var(--accent);
            font-weight: 700;
            text-decoration: none;
          }

          .endpoint a:hover { text-decoration: underline; }

          .footer-note {
            margin-top: 24px;
            font-size: 14px;
          }

          @media (max-width: 640px) {
            .hero { padding: 24px; }
            .lede { font-size: 16px; }
          }
        </style>
      </head>
      <body>
        <main class="shell">
          <section class="hero">
            <div class="eyebrow">OpenEnv Environment</div>
            <h1>METAMINDS ER Triage</h1>
            <p class="lede">
              A hospital emergency department triage simulator where an agent must classify urgency,
              handle resuscitation decisions, and use scarce beds safely across escalating tasks.
            </p>

            <div class="hero-grid">
              <div class="stat">
                <strong>3</strong>
                <span>deterministic tasks from easy to hard</span>
              </div>
              <div class="stat">
                <strong>OpenEnv</strong>
                <span>typed actions, observations, rewards, and state</span>
              </div>
              <div class="stat">
                <strong>API-First</strong>
                <span>ready for automated validation and agent evaluation</span>
              </div>
            </div>
          </section>

          <section class="section">
            <h2>Tasks</h2>
            <div class="task-grid">
              <article class="card">
                <h3>Single Patient</h3>
                <p>One patient, one triage choice. Focused on clear safety-critical classification.</p>
                <span class="pill">Easy</span>
              </article>
              <article class="card">
                <h3>Resource Aware</h3>
                <p>Queue pressure, scarce monitored beds, and pediatric or ambulance context.</p>
                <span class="pill">Medium</span>
              </article>
              <article class="card">
                <h3>Sequential Queue</h3>
                <p>Six-patient shift slice where consistent decision quality matters over time.</p>
                <span class="pill">Hard</span>
              </article>
            </div>
          </section>

          <section class="section">
            <h2>Endpoints</h2>
            <div class="endpoint-grid">
              <article class="endpoint">
                <h3><a href="/health">/health</a></h3>
                <p>Quick runtime status check.</p>
              </article>
              <article class="endpoint">
                <h3><a href="/metadata">/metadata</a></h3>
                <p>Environment metadata for validators and clients.</p>
              </article>
              <article class="endpoint">
                <h3><a href="/schema">/schema</a></h3>
                <p>Action, observation, and state schemas.</p>
              </article>
              <article class="endpoint">
                <h3><a href="/docs">/docs</a></h3>
                <p>FastAPI/OpenAPI interactive docs.</p>
              </article>
            </div>
          </section>

          <p class="footer-note">
            This Space is intentionally lightweight: the primary submission surface is the OpenEnv API rather than a custom UI.
          </p>
        </main>
      </body>
    </html>
    """


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
