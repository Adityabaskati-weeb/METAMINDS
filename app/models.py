from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TaskName(str, Enum):
    EASY = "single_patient"
    MEDIUM = "resource_aware"
    HARD = "sequential_queue"


class Vitals(BaseModel):
    heart_rate: int = Field(..., ge=0, le=220)
    blood_pressure_sys: int = Field(..., ge=0, le=300)
    blood_pressure_dia: int = Field(..., ge=0, le=200)
    oxygen_saturation: int = Field(..., ge=0, le=100)
    respiratory_rate: int = Field(..., ge=0, le=80)
    temperature_c: float = Field(..., ge=30.0, le=45.0)


class Observation(BaseModel):
    task: TaskName
    patient_id: str
    patient_complaint: str = Field(..., min_length=1, max_length=240)
    vitals: Vitals
    waiting_room: int = Field(default=0, ge=0)
    available_beds: int = Field(default=0, ge=0)
    previous_category: int = Field(default=0, ge=0, le=5)
    patients_remaining: int = Field(default=0, ge=0)
    notes: List[str] = Field(default_factory=list)


class Action(BaseModel):
    triage_category: int = Field(..., ge=1, le=5)
    send_to_resus: bool = False
    allocate_bed: bool = False


class Reward(BaseModel):
    value: float = Field(..., ge=-1.0, le=1.0)
    components: Dict[str, float] = Field(default_factory=dict)
    reasoning: str


class StepInfo(BaseModel):
    gold_category: int = Field(..., ge=1, le=5)
    patient_score: float = Field(..., ge=0.0, le=1.0)
    grader_score: float = Field(..., ge=0.0, le=1.0)
    critical_miss: bool = False
    task_completed: bool = False
    episode_metrics: Dict[str, float | int] = Field(default_factory=dict)


class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: StepInfo


class ResetRequest(BaseModel):
    task: TaskName = TaskName.EASY
    seed: int = Field(default=7, ge=0)


class ResetResponse(BaseModel):
    observation: Observation


class EpisodeState(BaseModel):
    episode_id: str
    task: TaskName
    step_count: int = Field(default=0, ge=0)
    delivered: int = Field(default=0, ge=0)
    score_so_far: float = Field(default=0.0, ge=0.0, le=1.0)
    done: bool = False
    metrics: Dict[str, float | int] = Field(default_factory=dict)


class BaselineRunResult(BaseModel):
    task: TaskName
    mean_score: float
    episode_scores: List[float]
    agent_name: Literal["heuristic", "openai"]

    @field_validator("mean_score")
    @classmethod
    def clamp_mean(cls, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 4)
