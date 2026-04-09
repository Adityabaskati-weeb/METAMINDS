from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

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

_demo_env = ERTriageEnvironment()


def _json_payload(observation: Observation) -> dict:
    return {
        "observation": observation.model_dump(mode="json"),
        "state": _demo_env.state.model_dump(mode="json"),
    }


@app.post("/demo/reset", include_in_schema=False)
async def demo_reset(request: Request) -> JSONResponse:
    payload = await request.json()
    try:
        observation = _demo_env.reset(
            seed=int(payload.get("seed", 0)),
            task=payload.get("task", "single_patient"),
        )
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    return JSONResponse(_json_payload(observation))


@app.post("/demo/step", include_in_schema=False)
async def demo_step(request: Request) -> JSONResponse:
    payload = await request.json()
    try:
        action = Action.model_validate(payload)
        observation = _demo_env.step(action)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    return JSONResponse(_json_payload(observation))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> str:
    return """
    <html>
      <head>
        <title>METAMINDS ER Triage</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          :root {
            --bg: #050805;
            --surface: rgba(8, 18, 10, 0.70);
            --surface-strong: rgba(8, 18, 10, 0.90);
            --text: #e8f5e9;
            --muted: #a5d6a7;
            --line: rgba(0, 153, 0, 0.18);
            --accent: #00cc66;
            --accent-dark: #003300;
            --accent-soft: rgba(0, 153, 0, 0.14);
            --ink: #a8dadc;
            --success: #00cc00;
            --warn: #ffb703;
            --danger: #e63946;
            --shadow: 0 4px 28px rgba(0,0,0,0.62);
          }

          * { box-sizing: border-box; }

          body {
            margin: 0;
            font-family: "Inter", "Segoe UI", "Aptos", sans-serif;
            color: var(--text);
            background:
              radial-gradient(ellipse at 15% 25%, rgba(0,153,0,0.10) 0%, transparent 48%),
              radial-gradient(ellipse at 85% 75%, rgba(0,204,102,0.07) 0%, transparent 48%),
              linear-gradient(180deg, #050805 0%, #071107 100%);
          }

          .shell {
            max-width: 1460px;
            margin: 0 auto;
            padding: 14px;
          }

          .topbar {
            position: sticky;
            top: 0;
            z-index: 20;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin: -14px -14px 14px;
            padding: 10px 24px;
            background: rgba(5, 8, 5, 0.90);
            border-bottom: 1px solid var(--line);
            backdrop-filter: blur(18px) saturate(140%);
          }

          .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 800;
            letter-spacing: -0.02em;
          }

          .brand-mark {
            width: 34px;
            height: 34px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--success), var(--accent-dark));
            color: white;
            font-weight: 900;
          }

          .status {
            padding: 8px 12px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.03);
            color: var(--success);
            font-size: 13px;
            font-weight: 800;
          }

          .hero {
            background: linear-gradient(135deg, rgba(8,18,10,0.94), rgba(8,18,10,0.68));
            border: 1px solid var(--line);
            border-radius: 10px;
            box-shadow: var(--shadow);
            padding: 22px;
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
            background: radial-gradient(circle, rgba(0, 204, 102, 0.18), transparent 65%);
          }

          .eyebrow {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(0,153,0,0.15);
            color: var(--success);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 14px;
          }

          h1 {
            margin: 0 0 12px;
            font-size: clamp(32px, 4vw, 48px);
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
          .demo-grid,
          .task-grid,
          .endpoint-grid {
            display: grid;
            gap: 16px;
            margin-top: 26px;
          }

          .hero-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
          .demo-grid { grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr); align-items: start; }
          .task-grid { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
          .endpoint-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

          .stat,
          .card,
          .panel,
          .endpoint {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 18px;
            backdrop-filter: blur(10px);
          }

          .stat:hover,
          .card:hover,
          .panel:hover,
          .endpoint:hover {
            border-color: rgba(0, 204, 0, 0.36);
            box-shadow: 0 0 18px rgba(0,153,0,0.09);
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

          .panel {
            padding: 20px;
          }

          .command-layout {
            display: grid;
            grid-template-columns: minmax(0, 1.45fr) minmax(340px, 0.55fr);
            gap: 16px;
            margin-top: 16px;
            align-items: stretch;
          }

          .flow-map {
            position: relative;
            min-height: 360px;
            border-radius: 10px;
            overflow: hidden;
            background:
              linear-gradient(rgba(0,153,0,0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0,153,0,0.05) 1px, transparent 1px),
              radial-gradient(circle at center, rgba(0,204,0,0.08), transparent 58%),
              rgba(5, 8, 5, 0.70);
            background-size: 36px 36px, 36px 36px, auto, auto;
            border: 1px solid var(--line);
          }

          .flow-edge {
            position: absolute;
            height: 2px;
            transform-origin: left center;
            background: linear-gradient(90deg, rgba(0,204,0,0.08), rgba(0,204,0,0.65), rgba(0,204,0,0.08));
            box-shadow: 0 0 12px rgba(0,204,0,0.20);
          }

          .flow-node {
            position: absolute;
            width: 112px;
            min-height: 72px;
            transform: translate(-50%, -50%);
            display: grid;
            place-items: center;
            text-align: center;
            gap: 4px;
            padding: 10px;
            border-radius: 14px;
            background: rgba(8, 18, 10, 0.92);
            border: 1px solid rgba(0,204,0,0.26);
            box-shadow: 0 0 22px rgba(0,153,0,0.12);
          }

          .flow-node strong {
            display: block;
            color: var(--text);
            font-size: 13px;
          }

          .flow-node span {
            color: var(--muted);
            font-size: 11px;
            font-weight: 700;
          }

          .flow-node.hot {
            border-color: rgba(230,57,70,0.62);
            box-shadow: 0 0 24px rgba(230,57,70,0.22);
          }

          .flow-node.warn {
            border-color: rgba(255,183,3,0.62);
            box-shadow: 0 0 24px rgba(255,183,3,0.18);
          }

          .flow-node.good {
            border-color: rgba(0,204,0,0.62);
          }

          .pulse-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 10px var(--success);
            animation: blink 1.2s infinite;
          }

          @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

          .panel h3 {
            margin: 0 0 12px;
            font-size: 20px;
          }

          .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 14px;
          }

          label {
            display: grid;
            gap: 6px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.07em;
          }

          select,
          input {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #071107;
            padding: 11px 36px 11px 12px;
            color: var(--text);
            font: inherit;
            color-scheme: dark;
          }

          select {
            appearance: none;
            background-image:
              linear-gradient(45deg, transparent 50%, var(--success) 50%),
              linear-gradient(135deg, var(--success) 50%, transparent 50%),
              linear-gradient(to right, rgba(0,204,0,0.16), rgba(0,204,0,0.16));
            background-position:
              calc(100% - 18px) 50%,
              calc(100% - 12px) 50%,
              calc(100% - 34px) 50%;
            background-size:
              6px 6px,
              6px 6px,
              1px 60%;
            background-repeat: no-repeat;
          }

          select:focus,
          input:focus {
            outline: none;
            border-color: var(--success);
            box-shadow: 0 0 0 3px rgba(0,204,0,0.16);
          }

          select option {
            background: #071107;
            color: #e8f5e9;
          }

          select option:checked,
          select option:hover {
            background: #003300;
            color: #ffffff;
          }

          .button-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 12px 0 4px;
          }

          button {
            border: 0;
            border-radius: 6px;
            padding: 11px 15px;
            cursor: pointer;
            background: rgba(0,153,0,0.18);
            color: white;
            font-weight: 800;
            font: inherit;
            border: 1px solid rgba(0,204,0,0.28);
            box-shadow: none;
          }

          button.secondary {
            background: rgba(168,218,220,0.12);
            color: var(--ink);
            border-color: rgba(168,218,220,0.26);
          }

          button.ghost {
            background: rgba(255,183,3,0.12);
            color: var(--warn);
            border-color: rgba(255,183,3,0.24);
            box-shadow: none;
          }

          .patient-card {
            border-radius: 10px;
            background: var(--surface-strong);
            border: 1px solid var(--line);
            padding: 18px;
            min-height: 260px;
          }

          .patient-title {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: flex-start;
            margin-bottom: 14px;
          }

          .patient-title h3 {
            margin: 0;
            font-size: clamp(22px, 3vw, 30px);
            letter-spacing: -0.03em;
          }

          .badge {
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(0,153,0,0.16);
            color: var(--success);
            font-size: 12px;
            font-weight: 900;
            white-space: nowrap;
          }

          .vitals {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
            gap: 10px;
            margin-top: 16px;
          }

          .vital {
            border: 1px solid rgba(23, 63, 69, 0.12);
            border-radius: 8px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.03);
          }

          .vital span {
            color: var(--muted);
            display: block;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            font-weight: 800;
          }

          .vital strong {
            display: block;
            margin-top: 5px;
            font-size: 20px;
          }

          .notes {
            margin: 14px 0 0;
            padding-left: 18px;
            color: var(--muted);
          }

          .result {
            margin-top: 12px;
            padding: 14px;
            border-radius: 16px;
            background: rgba(0,204,0,0.10);
            border: 1px solid rgba(0,204,0,0.22);
            color: var(--text);
            font-weight: 800;
          }

          .error-box {
            margin-top: 12px;
            padding: 14px;
            border-radius: 16px;
            background: rgba(230,57,70,0.10);
            border: 1px solid rgba(230,57,70,0.22);
            color: var(--danger);
            font-weight: 800;
          }

          .resource-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
          }

          .resource-tile {
            min-height: 112px;
            border-radius: 18px;
            padding: 14px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--line);
            position: relative;
            overflow: hidden;
          }

          .resource-tile::after {
            content: "";
            position: absolute;
            inset: auto -20px -32px auto;
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: rgba(180, 53, 44, 0.10);
          }

          .resource-tile span {
            color: var(--muted);
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.07em;
            text-transform: uppercase;
          }

          .resource-tile strong {
            display: block;
            margin-top: 10px;
            font-size: 34px;
            letter-spacing: -0.04em;
          }

          .queue-bars {
            display: grid;
            gap: 10px;
          }

          .queue-row {
            display: grid;
            grid-template-columns: 72px 1fr 42px;
            gap: 10px;
            align-items: center;
          }

          .queue-label {
            color: var(--muted);
            font-size: 12px;
            font-weight: 900;
          }

          .bar-shell {
            height: 12px;
            border-radius: 999px;
            background: rgba(23, 63, 69, 0.10);
            overflow: hidden;
          }

          .bar-fill {
            height: 100%;
            min-width: 4px;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--accent), var(--warn));
          }

          .score-card {
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 18px;
            align-items: center;
          }

          .score-ring {
            width: 112px;
            height: 112px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background:
              radial-gradient(circle at center, white 0 56%, transparent 57%),
              conic-gradient(var(--success) calc(var(--score, 0) * 1%), rgba(23,63,69,0.12) 0);
            border: 1px solid var(--line);
            font-size: 24px;
            font-weight: 900;
            color: var(--success);
          }

          .component-list {
            display: grid;
            gap: 9px;
          }

          .component {
            display: grid;
            grid-template-columns: minmax(110px, 1fr) 60px;
            gap: 10px;
            align-items: center;
            color: var(--muted);
            font-size: 13px;
          }

          .component strong {
            color: var(--text);
            text-align: right;
          }

          .grader-note {
            margin-top: 14px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.55;
          }

          pre {
            white-space: pre-wrap;
            overflow: auto;
            max-height: 320px;
            margin: 0;
            background: #020502;
            color: #e8f5e9;
            border-radius: 8px;
            padding: 16px;
            font-size: 12px;
            line-height: 1.5;
            border: 1px solid rgba(0,153,0,0.14);
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
            background: rgba(0,153,0,0.14);
            color: var(--success);
            font-size: 12px;
            font-weight: 700;
          }

          .endpoint a {
            color: var(--success);
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
            .demo-grid { grid-template-columns: 1fr; }
            .command-layout { grid-template-columns: 1fr; }
            .patient-title { display: block; }
            .badge { margin-top: 10px; }
          }
        </style>
      </head>
      <body>
        <main class="shell">
          <div class="topbar">
            <div class="brand"><span class="brand-mark">ER</span> METAMINDS</div>
            <div class="status">Running</div>
          </div>

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
            <h2>Interactive Demo</h2>
            <div class="command-layout">
              <div class="panel">
                <h3>ER Flow Topology</h3>
                <div class="flow-map" id="flowMap">
                  <div class="flow-edge" style="left: 18%; top: 30%; width: 24%; transform: rotate(14deg);"></div>
                  <div class="flow-edge" style="left: 40%; top: 38%; width: 24%; transform: rotate(-18deg);"></div>
                  <div class="flow-edge" style="left: 41%; top: 42%; width: 25%; transform: rotate(22deg);"></div>
                  <div class="flow-edge" style="left: 18%; top: 67%; width: 26%; transform: rotate(-16deg);"></div>
                  <div class="flow-edge" style="left: 58%; top: 56%; width: 22%; transform: rotate(4deg);"></div>
                  <div class="flow-node good" style="left: 15%; top: 32%;">
                    <div class="pulse-dot"></div>
                    <strong>Ambulance</strong>
                    <span id="flowArrival">-</span>
                  </div>
                  <div class="flow-node warn" style="left: 42%; top: 42%;">
                    <strong>Triage Desk</strong>
                    <span id="flowTriage">Awaiting decision</span>
                  </div>
                  <div class="flow-node hot" style="left: 72%; top: 30%;">
                    <strong>Resus Bay</strong>
                    <span id="flowResus">-</span>
                  </div>
                  <div class="flow-node good" style="left: 74%; top: 62%;">
                    <strong>Monitored Beds</strong>
                    <span id="flowBeds">-</span>
                  </div>
                  <div class="flow-node warn" style="left: 24%; top: 74%;">
                    <strong>Waiting Room</strong>
                    <span id="flowWaiting">-</span>
                  </div>
                </div>
              </div>

              <div class="panel">
                <h3>Command Metrics</h3>
                <div class="resource-grid">
                  <div class="resource-tile">
                    <span>Current Reward</span>
                    <strong id="metricReward">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Patient Score</span>
                    <strong id="metricPatientScore">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Gold Category</span>
                    <strong id="metricGold">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Critical Miss</span>
                    <strong id="metricCritical">-</strong>
                  </div>
                </div>
              </div>
            </div>
            <div class="demo-grid">
              <div class="panel">
                <div class="controls">
                  <label>
                    Task
                    <select id="task">
                      <option value="single_patient">Single Patient</option>
                      <option value="resource_aware">Resource Aware</option>
                      <option value="sequential_queue">Sequential Queue</option>
                    </select>
                  </label>
                  <label>
                    Seed
                    <input id="seed" type="number" value="0" min="0" />
                  </label>
                  <label>
                    Triage Category
                    <select id="triage">
                      <option value="1">1 - Immediate</option>
                      <option value="2">2 - Emergent</option>
                      <option value="3">3 - Urgent</option>
                      <option value="4">4 - Less urgent</option>
                      <option value="5">5 - Non-urgent</option>
                    </select>
                  </label>
                  <label>
                    Send to Resus
                    <select id="resus">
                      <option value="true">true</option>
                      <option value="false">false</option>
                    </select>
                  </label>
                  <label>
                    Allocate Bed
                    <select id="bed">
                      <option value="true">true</option>
                      <option value="false">false</option>
                    </select>
                  </label>
                </div>
                <div class="button-row">
                  <button onclick="resetDemo()">Reset Episode</button>
                  <button class="secondary" onclick="stepDemo()">Submit Action</button>
                  <button class="ghost" onclick="suggestAction()">Suggest Safe Action</button>
                </div>
                <div id="result"></div>
              </div>

              <div class="patient-card">
                <div class="patient-title">
                  <h3 id="complaint">Press Reset Episode to start.</h3>
                  <span class="badge" id="taskBadge">No active patient</span>
                </div>
                <p id="context">The demo uses the same deterministic environment engine as the OpenEnv API.</p>
                <div class="vitals" id="vitals"></div>
                <ul class="notes" id="notes"></ul>
              </div>
            </div>

            <div class="demo-grid">
              <div class="panel">
                <h3>Resource Monitor</h3>
                <div class="resource-grid">
                  <div class="resource-tile">
                    <span>Available Beds</span>
                    <strong id="bedCount">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Waiting Room</span>
                    <strong id="waitingCount">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Remaining Patients</span>
                    <strong id="remainingCount">-</strong>
                  </div>
                  <div class="resource-tile">
                    <span>Shift Minutes</span>
                    <strong id="shiftMinutes">-</strong>
                  </div>
                </div>
              </div>

              <div class="panel">
                <h3>Acuity Queue</h3>
                <div class="queue-bars" id="queueBars"></div>
              </div>
            </div>

            <div class="demo-grid">
              <div class="panel">
                <h3>Reward Breakdown</h3>
                <div class="score-card">
                  <div class="score-ring" id="scoreRing" style="--score: 0">-</div>
                  <div>
                    <div class="component-list" id="componentList">
                      <div class="component"><span>No reward yet</span><strong>-</strong></div>
                    </div>
                    <p class="grader-note" id="graderNote">
                      Submit an action to reveal grader feedback, gold triage category, and safety penalties.
                    </p>
                  </div>
                </div>
              </div>

              <div class="panel">
                <h3>Episode Metrics</h3>
                <div class="component-list" id="metricList">
                  <div class="component"><span>No episode metrics yet</span><strong>-</strong></div>
                </div>
              </div>
            </div>

            <div class="demo-grid">
              <div class="panel">
                <h3>State</h3>
                <pre id="stateBox">{}</pre>
              </div>
              <div class="panel">
                <h3>Observation</h3>
                <pre id="obsBox">{}</pre>
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
            The demo is a convenience layer. Automated evaluation should still use the standard OpenEnv endpoints.
          </p>
        </main>
        <script>
          let currentObservation = null;

          function boolValue(id) {
            return document.getElementById(id).value === "true";
          }

          function actionPayload() {
            return {
              triage_category: Number(document.getElementById("triage").value),
              send_to_resus: boolValue("resus"),
              allocate_bed: boolValue("bed")
            };
          }

          function setAction(category, resus, bed) {
            document.getElementById("triage").value = String(category);
            document.getElementById("resus").value = String(resus);
            document.getElementById("bed").value = String(bed);
          }

          function suggestedFromObservation(obs) {
            const v = obs.vitals || {};
            const complaint = (obs.patient_complaint || "").toLowerCase();
            const notes = (obs.notes || []).join(" ").toLowerCase();
            const unstable =
              v.oxygen_saturation < 90 ||
              v.blood_pressure_sys < 90 ||
              v.respiratory_rate > 32 ||
              obs.mental_status.toLowerCase() !== "alert";
            const highRisk =
              complaint.includes("stroke") ||
              complaint.includes("chest") ||
              complaint.includes("sepsis") ||
              complaint.includes("bleeding") ||
              notes.includes("shock");
            if (unstable) return { triage_category: 1, send_to_resus: true, allocate_bed: obs.available_beds > 0 };
            if (highRisk) return { triage_category: 2, send_to_resus: true, allocate_bed: obs.available_beds > 0 };
            if (obs.pain_score >= 7 || v.heart_rate > 120) {
              return { triage_category: 3, send_to_resus: false, allocate_bed: obs.available_beds > 0 };
            }
            return { triage_category: 4, send_to_resus: false, allocate_bed: false };
          }

          function suggestAction() {
            if (!currentObservation) {
              showMessage("Reset an episode before requesting a suggested action.", true);
              return;
            }
            const action = suggestedFromObservation(currentObservation);
            setAction(action.triage_category, action.send_to_resus, action.allocate_bed);
            showMessage("Suggested a safety-oriented action from vitals, complaint, and resource context.", false);
          }

          function showMessage(text, isError) {
            const result = document.getElementById("result");
            result.className = isError ? "error-box" : "result";
            result.textContent = text;
          }

          function renderResourceMonitor(obs, state) {
            document.getElementById("bedCount").textContent = obs.available_beds;
            document.getElementById("waitingCount").textContent = obs.waiting_room;
            document.getElementById("remainingCount").textContent = obs.patients_remaining;
            document.getElementById("shiftMinutes").textContent = obs.elapsed_shift_minutes;

            const queue = obs.queue_by_acuity || [];
            const maxQueue = Math.max(1, ...queue);
            document.getElementById("queueBars").innerHTML = [1, 2, 3, 4, 5].map((acuity, index) => {
              const value = Number(queue[index] || 0);
              const width = Math.max(4, Math.round((value / maxQueue) * 100));
              return `
                <div class="queue-row">
                  <div class="queue-label">Level ${acuity}</div>
                  <div class="bar-shell"><div class="bar-fill" style="width: ${width}%"></div></div>
                  <strong>${value}</strong>
                </div>
              `;
            }).join("");

            const metrics = (state && state.metrics) || {};
            const metricEntries = Object.entries(metrics);
            document.getElementById("metricList").innerHTML = metricEntries.length
              ? metricEntries.map(([key, value]) => `
                  <div class="component"><span>${key.replaceAll("_", " ")}</span><strong>${value}</strong></div>
                `).join("")
              : '<div class="component"><span>No episode metrics yet</span><strong>-</strong></div>';
          }

          function renderRewardBreakdown(obs) {
            const metadata = obs.metadata || {};
            const components = metadata.reward_components || {};
            const grader = metadata.grader || {};
            const reward = typeof obs.reward === "number" ? obs.reward : null;
            const normalized = reward === null ? 0 : Math.max(0, Math.min(100, Math.round(((reward + 1) / 2) * 100)));
            const ring = document.getElementById("scoreRing");
            ring.style.setProperty("--score", normalized);
            ring.textContent = reward === null ? "-" : reward.toFixed(2);

            const entries = Object.entries(components);
            document.getElementById("componentList").innerHTML = entries.length
              ? entries.map(([key, value]) => `
                  <div class="component"><span>${key.replaceAll("_", " ")}</span><strong>${Number(value).toFixed(2)}</strong></div>
                `).join("")
              : '<div class="component"><span>No reward yet</span><strong>-</strong></div>';

            const gold = grader.gold_category ? `Gold category ${grader.gold_category}` : "Gold category hidden until first step";
            const patientScore = typeof grader.patient_score === "number"
              ? `patient score ${grader.patient_score.toFixed(2)}`
              : "patient score pending";
            const critical = grader.critical_miss ? "critical miss detected" : "no critical miss";
            document.getElementById("graderNote").textContent = `${gold}; ${patientScore}; ${critical}.`;
          }

          function renderFlowMap(obs) {
            const metadata = obs.metadata || {};
            const grader = metadata.grader || {};
            document.getElementById("flowArrival").textContent = obs.arrival_mode || "-";
            document.getElementById("flowTriage").textContent = obs.done ? "Episode complete" : `Next decision: CAT ${obs.previous_category || "-"}`;
            document.getElementById("flowResus").textContent = obs.mental_status === "alert" ? "standby" : "attention needed";
            document.getElementById("flowBeds").textContent = `${obs.available_beds} open`;
            document.getElementById("flowWaiting").textContent = `${obs.waiting_room} waiting`;
            document.getElementById("metricReward").textContent =
              typeof obs.reward === "number" ? obs.reward.toFixed(2) : "-";
            document.getElementById("metricPatientScore").textContent =
              typeof grader.patient_score === "number" ? grader.patient_score.toFixed(2) : "-";
            document.getElementById("metricGold").textContent = grader.gold_category || "-";
            document.getElementById("metricCritical").textContent = grader.critical_miss ? "YES" : "NO";
          }

          function render(payload) {
            if (payload.error) {
              showMessage(payload.error, true);
              return;
            }
            const obs = payload.observation;
            const state = payload.state;
            currentObservation = obs;
            document.getElementById("complaint").textContent = obs.patient_complaint;
            document.getElementById("taskBadge").textContent = `${obs.task} - patient ${obs.patient_id}`;
            document.getElementById("context").textContent =
              `${obs.age_years} years, ${obs.arrival_mode}, mental status: ${obs.mental_status}, ` +
              `waiting room: ${obs.waiting_room}, beds: ${obs.available_beds}, remaining: ${obs.patients_remaining}`;

            const vitals = obs.vitals || {};
            document.getElementById("vitals").innerHTML = `
              <div class="vital"><span>Heart Rate</span><strong>${vitals.heart_rate}</strong></div>
              <div class="vital"><span>Blood Pressure</span><strong>${vitals.blood_pressure_sys}/${vitals.blood_pressure_dia}</strong></div>
              <div class="vital"><span>Oxygen</span><strong>${vitals.oxygen_saturation}%</strong></div>
              <div class="vital"><span>Resp Rate</span><strong>${vitals.respiratory_rate}</strong></div>
              <div class="vital"><span>Temperature</span><strong>${vitals.temperature_c} C</strong></div>
              <div class="vital"><span>Pain</span><strong>${obs.pain_score}/10</strong></div>
            `;
            document.getElementById("notes").innerHTML = (obs.notes || []).map(note => `<li>${note}</li>`).join("");
            document.getElementById("stateBox").textContent = JSON.stringify(state, null, 2);
            document.getElementById("obsBox").textContent = JSON.stringify(obs, null, 2);
            renderResourceMonitor(obs, state);
            renderRewardBreakdown(obs);
            renderFlowMap(obs);

            if (typeof obs.reward === "number") {
              showMessage(`Reward ${obs.reward.toFixed(2)} | done=${obs.done}`, false);
            }
          }

          async function postJson(url, payload) {
            const response = await fetch(url, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            return await response.json();
          }

          async function resetDemo() {
            const payload = {
              task: document.getElementById("task").value,
              seed: Number(document.getElementById("seed").value)
            };
            const data = await postJson("/demo/reset", payload);
            render(data);
            if (!data.error) suggestAction();
          }

          async function stepDemo() {
            const data = await postJson("/demo/step", actionPayload());
            render(data);
            if (!data.error && !data.observation.done) {
              const next = suggestedFromObservation(data.observation);
              setAction(next.triage_category, next.send_to_resus, next.allocate_bed);
            }
          }

          resetDemo();
        </script>
      </body>
    </html>
    """


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
