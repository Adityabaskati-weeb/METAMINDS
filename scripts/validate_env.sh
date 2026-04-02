#!/usr/bin/env bash
set -euo pipefail

python -m pytest
openenv validate --json
python scripts/validate_submission.py
