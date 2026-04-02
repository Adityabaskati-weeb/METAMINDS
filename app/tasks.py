from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from app.models import TaskName


TASK_DATA: Dict[TaskName, List[dict]] = {
    TaskName.EASY: [
        {
            "patient_id": "easy-1",
            "patient_complaint": "Crushing chest pain and sweating",
            "vitals": {
                "heart_rate": 118,
                "blood_pressure_sys": 84,
                "blood_pressure_dia": 56,
                "oxygen_saturation": 91,
                "respiratory_rate": 26,
                "temperature_c": 36.8,
            },
            "waiting_room": 2,
            "available_beds": 1,
            "gold_category": 1,
            "requires_resus": True,
            "bed_required": True,
            "notes": ["Possible acute coronary syndrome", "High-risk hypotension"],
        }
    ],
    TaskName.MEDIUM: [
        {
            "patient_id": "med-1",
            "patient_complaint": "Shortness of breath with audible wheeze",
            "vitals": {
                "heart_rate": 124,
                "blood_pressure_sys": 96,
                "blood_pressure_dia": 64,
                "oxygen_saturation": 88,
                "respiratory_rate": 30,
                "temperature_c": 37.1,
            },
            "waiting_room": 11,
            "available_beds": 0,
            "gold_category": 2,
            "requires_resus": True,
            "bed_required": False,
            "notes": ["Possible severe asthma exacerbation", "No monitored beds free"],
        }
    ],
    TaskName.HARD: [
        {
            "patient_id": "hard-1",
            "patient_complaint": "Unresponsive after collapse in waiting area",
            "vitals": {
                "heart_rate": 42,
                "blood_pressure_sys": 70,
                "blood_pressure_dia": 40,
                "oxygen_saturation": 82,
                "respiratory_rate": 8,
                "temperature_c": 36.2,
            },
            "waiting_room": 7,
            "available_beds": 0,
            "gold_category": 1,
            "requires_resus": True,
            "bed_required": False,
            "notes": ["Immediate intervention needed"],
        },
        {
            "patient_id": "hard-2",
            "patient_complaint": "Fever, rigors, confusion",
            "vitals": {
                "heart_rate": 132,
                "blood_pressure_sys": 92,
                "blood_pressure_dia": 58,
                "oxygen_saturation": 94,
                "respiratory_rate": 24,
                "temperature_c": 39.4,
            },
            "waiting_room": 8,
            "available_beds": 1,
            "gold_category": 2,
            "requires_resus": False,
            "bed_required": True,
            "notes": ["Sepsis concern"],
        },
        {
            "patient_id": "hard-3",
            "patient_complaint": "Severe abdominal pain radiating to back",
            "vitals": {
                "heart_rate": 108,
                "blood_pressure_sys": 104,
                "blood_pressure_dia": 66,
                "oxygen_saturation": 97,
                "respiratory_rate": 22,
                "temperature_c": 37.6,
            },
            "waiting_room": 9,
            "available_beds": 1,
            "gold_category": 3,
            "requires_resus": False,
            "bed_required": False,
            "notes": ["Urgent imaging likely"],
        },
        {
            "patient_id": "hard-4",
            "patient_complaint": "Ankle injury after sports practice",
            "vitals": {
                "heart_rate": 88,
                "blood_pressure_sys": 122,
                "blood_pressure_dia": 78,
                "oxygen_saturation": 99,
                "respiratory_rate": 16,
                "temperature_c": 36.7,
            },
            "waiting_room": 10,
            "available_beds": 0,
            "gold_category": 5,
            "requires_resus": False,
            "bed_required": False,
            "notes": ["Likely stable musculoskeletal injury"],
        },
        {
            "patient_id": "hard-5",
            "patient_complaint": "Slurred speech and unilateral weakness",
            "vitals": {
                "heart_rate": 98,
                "blood_pressure_sys": 168,
                "blood_pressure_dia": 96,
                "oxygen_saturation": 95,
                "respiratory_rate": 20,
                "temperature_c": 36.9,
            },
            "waiting_room": 11,
            "available_beds": 1,
            "gold_category": 2,
            "requires_resus": True,
            "bed_required": True,
            "notes": ["Possible acute stroke"],
        },
    ],
}


def load_task_cases(task: TaskName) -> List[dict]:
    return deepcopy(TASK_DATA[task])
