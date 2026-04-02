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

    subprocess.run(
        [sys.executable, "inference.py", "--smoke-run"],
        cwd=ROOT,
        check=True,
    )
    print("Submission validation checks passed.")


if __name__ == "__main__":
    main()
