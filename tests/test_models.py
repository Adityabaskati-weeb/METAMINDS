from app.models import Action, Observation, TaskName, Vitals


def test_action_bounds() -> None:
    action = Action(triage_category=3, send_to_resus=False, allocate_bed=False)
    assert action.triage_category == 3


def test_observation_creation() -> None:
    observation = Observation(
        task=TaskName.EASY,
        patient_id="p1",
        patient_complaint="Headache",
        age_years=28,
        arrival_mode="walk-in",
        mental_status="alert",
        pain_score=3,
        vitals=Vitals(
            heart_rate=85,
            blood_pressure_sys=120,
            blood_pressure_dia=80,
            oxygen_saturation=99,
            respiratory_rate=16,
            temperature_c=36.8,
        ),
        queue_by_acuity=[0, 1, 2],
        elapsed_shift_minutes=120,
    )
    assert observation.patient_id == "p1"
