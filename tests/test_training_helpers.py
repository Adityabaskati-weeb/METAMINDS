import json

from app.models import Observation, TaskName, Vitals
from training.er_triage_grpo import extract_json_block, observation_to_prompt, parse_action_response


def _sample_observation() -> Observation:
    return Observation(
        task=TaskName.MEDIUM,
        patient_id="case-1",
        patient_complaint="Shortness of breath with wheeze",
        age_years=26,
        arrival_mode="walk-in",
        mental_status="anxious",
        pain_score=4,
        vitals=Vitals(
            heart_rate=124,
            blood_pressure_sys=96,
            blood_pressure_dia=64,
            oxygen_saturation=88,
            respiratory_rate=30,
            temperature_c=37.1,
        ),
        waiting_room=11,
        available_beds=0,
        queue_by_acuity=[0, 2, 4, 3, 2],
        elapsed_shift_minutes=340,
        previous_category=0,
        patients_remaining=0,
        notes=["Severe asthma exacerbation"],
    )


def test_observation_to_prompt_contains_core_fields() -> None:
    prompt = observation_to_prompt(_sample_observation())
    assert "Shortness of breath with wheeze" in prompt
    assert "Available beds: 0" in prompt
    assert "Queue by acuity" in prompt


def test_parse_action_response_extracts_json() -> None:
    action = parse_action_response('Answer: {"triage_category": 2, "send_to_resus": true, "allocate_bed": false}')
    assert action.triage_category == 2
    assert action.send_to_resus is True
    assert action.allocate_bed is False


def test_extract_json_block_is_valid_json() -> None:
    block = extract_json_block('prefix {"triage_category": 3, "send_to_resus": false, "allocate_bed": true} suffix')
    payload = json.loads(block)
    assert payload["triage_category"] == 3
