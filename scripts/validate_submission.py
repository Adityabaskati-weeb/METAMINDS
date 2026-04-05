from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ENV_VARS = ("API_BASE_URL", "MODEL_NAME", "HF_TOKEN")
REQUIRED_FILES = ("inference.py", "openenv.yaml", "Dockerfile")


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    for file_name in REQUIRED_FILES:
        _ensure((ROOT / file_name).exists(), f"Missing required file: {file_name}")

    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    _ensure(not missing, f"Missing required environment variables: {', '.join(missing)}")

    completed = subprocess.run(
        [sys.executable, "inference.py", "--smoke-run"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    _ensure(completed.returncode == 0, "inference.py smoke run failed")

    stdout_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    _ensure(len(stdout_lines) >= 3, "inference.py did not emit the required START/STEP/END lines")
    _ensure(stdout_lines[0].startswith("[START] "), "First stdout line must be [START]")
    _ensure(any(line.startswith("[STEP] ") for line in stdout_lines), "inference.py must emit at least one [STEP] line")
    end_lines = [line for line in stdout_lines if line.startswith("[END] ")]
    _ensure(len(end_lines) == 1, "inference.py must emit exactly one [END] line")
    _ensure("success=true" in end_lines[0], "inference.py smoke run did not finish successfully")
    _ensure(" score=" in end_lines[0], "inference.py [END] line must include score=<score>")
    print("Submission validation checks passed.")


if __name__ == "__main__":
    main()
