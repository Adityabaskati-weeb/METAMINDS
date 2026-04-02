#!/usr/bin/env bash
set -euo pipefail

python -m pytest
# If openenv is installed in the runtime, add:
# openenv validate .
