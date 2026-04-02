from fastapi.testclient import TestClient

from app.server import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_reset_and_state() -> None:
    reset_response = client.post("/reset", json={"task": "single_patient", "seed": 7})
    assert reset_response.status_code == 200
    state_response = client.get("/state")
    assert state_response.status_code == 200
    assert state_response.json()["task"] == "single_patient"
