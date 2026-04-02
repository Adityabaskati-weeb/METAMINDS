from fastapi.testclient import TestClient

from server.app import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_reset_and_state() -> None:
    reset_response = client.post("/reset", json={"task": "single_patient", "seed": 7})
    assert reset_response.status_code == 200
    assert "observation" in reset_response.json()
    state_response = client.get("/state")
    assert state_response.status_code == 200
    assert "episode_id" in state_response.json()
    assert state_response.json()["step_count"] == 0


def test_metadata_and_schema() -> None:
    metadata_response = client.get("/metadata")
    assert metadata_response.status_code == 200
    assert metadata_response.json()["name"] == "METAMINDS ER Triage"

    schema_response = client.get("/schema")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    assert "action" in schema
    assert "observation" in schema
    assert "state" in schema
