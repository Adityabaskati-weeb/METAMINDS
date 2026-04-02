from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.models import Action, Observation, TaskName, Vitals
from app.tasks import iter_task_episodes

MODEL_DIR = Path("outputs/models")
EVAL_DIR = Path("outputs/evals")
MODEL_PATH = MODEL_DIR / "er_triage_policy.joblib"
REPORT_PATH = EVAL_DIR / "training_report.json"

ARRIVAL_FEATURES = ("walk-in", "ambulance", "wheelchair", "carried", "collapse")
MENTAL_STATUS_FEATURES = ("alert", "anxious", "confused", "drowsy", "unresponsive", "frightened", "oriented")
COMPLAINT_KEYWORDS = (
    "chest pain",
    "stroke",
    "weakness",
    "wheeze",
    "stridor",
    "fever",
    "bleeding",
    "ankle",
    "trauma",
    "allergy",
)


def case_to_observation(task: TaskName, case: dict, previous_category: int = 0, patients_remaining: int = 0) -> Observation:
    return Observation(
        task=task,
        patient_id=case["patient_id"],
        patient_complaint=case["patient_complaint"],
        age_years=case["age_years"],
        arrival_mode=case["arrival_mode"],
        mental_status=case["mental_status"],
        pain_score=case["pain_score"],
        vitals=Vitals(**case["vitals"]),
        waiting_room=case["waiting_room"],
        available_beds=case["available_beds"],
        queue_by_acuity=case.get("queue_by_acuity", []),
        elapsed_shift_minutes=case.get("elapsed_shift_minutes", 0),
        previous_category=previous_category,
        patients_remaining=patients_remaining,
        notes=case.get("notes", []),
    )


def observation_to_features(observation: Observation) -> np.ndarray:
    complaint = observation.patient_complaint.lower()
    arrival = observation.arrival_mode.lower()
    mental = observation.mental_status.lower()
    vitals = observation.vitals
    features: list[float] = [
        float(observation.age_years),
        float(observation.pain_score),
        float(vitals.heart_rate),
        float(vitals.blood_pressure_sys),
        float(vitals.blood_pressure_dia),
        float(vitals.oxygen_saturation),
        float(vitals.respiratory_rate),
        float(vitals.temperature_c),
        float(observation.waiting_room),
        float(observation.available_beds),
        float(observation.elapsed_shift_minutes),
        float(observation.previous_category),
        float(observation.patients_remaining),
    ]
    queue = observation.queue_by_acuity[:5] + [0] * max(0, 5 - len(observation.queue_by_acuity))
    features.extend(float(v) for v in queue[:5])
    features.extend(1.0 if token in arrival else 0.0 for token in ARRIVAL_FEATURES)
    features.extend(1.0 if token in mental else 0.0 for token in MENTAL_STATUS_FEATURES)
    features.extend(1.0 if token in complaint else 0.0 for token in COMPLAINT_KEYWORDS)
    return np.array(features, dtype=np.float32)


def case_to_labels(case: dict) -> tuple[int, int, int]:
    triage_category = int(case["gold_category"])
    send_to_resus = int(bool(case.get("requires_resus", False)))
    allocate_bed = int(bool(case.get("bed_required", False) and case.get("available_beds", 0) > 0))
    return triage_category, send_to_resus, allocate_bed


def build_training_matrix() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
    X: list[np.ndarray] = []
    y_triage: list[int] = []
    y_resus: list[int] = []
    y_bed: list[int] = []
    groups: list[str] = []

    for task, seed, episode in iter_task_episodes():
        for idx, case in enumerate(episode):
            observation = case_to_observation(
                task=task,
                case=case,
                previous_category=episode[idx - 1]["gold_category"] if idx > 0 else 0,
                patients_remaining=max(0, len(episode) - idx - 1),
            )
            triage_category, send_to_resus, allocate_bed = case_to_labels(case)
            X.append(observation_to_features(observation))
            y_triage.append(triage_category)
            y_resus.append(send_to_resus)
            y_bed.append(allocate_bed)
            groups.append(f"{task.value}:{seed}")

    return (
        np.vstack(X),
        np.array(y_triage),
        np.array(y_resus),
        np.array(y_bed),
        groups,
    )


def default_eval_groups() -> list[str]:
    return [
        "single_patient:2",
        "resource_aware:2",
        "sequential_queue:1",
    ]


def _fit_models(X: np.ndarray, y_triage: np.ndarray, y_resus: np.ndarray, y_bed: np.ndarray) -> dict[str, Any]:
    triage_model = RandomForestClassifier(n_estimators=100, random_state=7)
    resus_model = RandomForestClassifier(n_estimators=80, random_state=7)
    bed_model = RandomForestClassifier(n_estimators=80, random_state=7)
    triage_model.fit(X, y_triage)
    resus_model.fit(X, y_resus)
    bed_model.fit(X, y_bed)
    return {"triage": triage_model, "resus": resus_model, "bed": bed_model}


def train_and_save_policy(eval_groups: list[str] | None = None) -> dict[str, Any]:
    X, y_triage, y_resus, y_bed, groups = build_training_matrix()
    eval_groups = eval_groups or default_eval_groups()
    train_mask = np.array([g not in eval_groups for g in groups])
    test_mask = np.array([g in eval_groups for g in groups])

    final_models = _fit_models(X[train_mask], y_triage[train_mask], y_resus[train_mask], y_bed[train_mask])
    artifact = {
        "models": final_models,
        "feature_size": int(X.shape[1]),
        "training_examples": int(np.sum(train_mask)),
        "eval_groups": eval_groups,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)

    triage_pred = final_models["triage"].predict(X[test_mask])
    resus_pred = final_models["resus"].predict(X[test_mask])
    bed_pred = final_models["bed"].predict(X[test_mask])
    action_match = (
        (triage_pred == y_triage[test_mask])
        & (resus_pred == y_resus[test_mask])
        & (bed_pred == y_bed[test_mask])
    )

    group_reports: list[dict[str, Any]] = []
    for group in eval_groups:
        group_mask = np.array([g == group for g in groups])
        group_mask = group_mask & test_mask
        if not np.any(group_mask):
            continue
        group_reports.append(
            {
                "group": group,
                "triage_accuracy": round(float(np.mean(final_models["triage"].predict(X[group_mask]) == y_triage[group_mask])), 4),
                "resus_accuracy": round(float(np.mean(final_models["resus"].predict(X[group_mask]) == y_resus[group_mask])), 4),
                "bed_accuracy": round(float(np.mean(final_models["bed"].predict(X[group_mask]) == y_bed[group_mask])), 4),
                "exact_action_accuracy": round(
                    float(
                        np.mean(
                            (final_models["triage"].predict(X[group_mask]) == y_triage[group_mask])
                            & (final_models["resus"].predict(X[group_mask]) == y_resus[group_mask])
                            & (final_models["bed"].predict(X[group_mask]) == y_bed[group_mask])
                        )
                    ),
                    4,
                ),
                "cases": int(np.sum(group_mask)),
            }
        )

    report = {
        "artifact_path": str(MODEL_PATH),
        "training_examples": int(np.sum(train_mask)),
        "evaluation_examples": int(np.sum(test_mask)),
        "eval_groups": eval_groups,
        "group_reports": group_reports,
        "heldout_exact_action_accuracy": round(float(np.mean(action_match)), 4),
        "heldout_triage_accuracy": round(float(np.mean(triage_pred == y_triage[test_mask])), 4),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def load_policy_artifact(path: Path | str = MODEL_PATH) -> dict[str, Any]:
    return joblib.load(path)


def predict_action(observation: Observation, artifact: dict[str, Any] | None = None) -> Action:
    artifact = artifact or load_policy_artifact()
    features = observation_to_features(observation).reshape(1, -1)
    triage = int(artifact["models"]["triage"].predict(features)[0])
    send_to_resus = bool(artifact["models"]["resus"].predict(features)[0])
    allocate_bed = bool(artifact["models"]["bed"].predict(features)[0])
    return Action(
        triage_category=triage,
        send_to_resus=send_to_resus,
        allocate_bed=allocate_bed,
    )


def main() -> None:
    report = train_and_save_policy()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
