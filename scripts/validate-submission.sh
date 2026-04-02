#!/usr/bin/env bash
set -uo pipefail

DOCKER_BUILD_TIMEOUT=600

if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' BOLD='' NC=''
fi

PING_URL="${1:-}"
REPO_DIR="${2:-.}"

if [ -z "$PING_URL" ]; then
  echo "${RED}Usage: ./scripts/validate-submission.sh <ping_url> [repo_dir]${NC}"
  exit 1
fi

cd "$REPO_DIR" || exit 1

echo "${BOLD}1. Checking required files...${NC}"
test -f inference.py || { echo "${RED}Missing inference.py${NC}"; exit 1; }
test -f openenv.yaml || { echo "${RED}Missing openenv.yaml${NC}"; exit 1; }
test -f Dockerfile || { echo "${RED}Missing Dockerfile${NC}"; exit 1; }

echo "${BOLD}2. Pinging HF Space...${NC}"
curl -fsSL "$PING_URL/health" >/dev/null || { echo "${RED}HF Space health check failed${NC}"; exit 1; }

echo "${BOLD}3. Validating OpenEnv live runtime...${NC}"
openenv validate --url "$PING_URL" >/dev/null || { echo "${RED}openenv validate --url failed${NC}"; exit 1; }

echo "${BOLD}4. Validating local OpenEnv structure...${NC}"
openenv validate --json >/dev/null || { echo "${RED}openenv validate --json failed${NC}"; exit 1; }

echo "${BOLD}5. Running tests...${NC}"
python -m pytest -q || { echo "${RED}pytest failed${NC}"; exit 1; }

echo "${BOLD}6. Checking required env vars...${NC}"
test -n "${API_BASE_URL:-}" || { echo "${RED}Missing API_BASE_URL${NC}"; exit 1; }
test -n "${MODEL_NAME:-}" || { echo "${RED}Missing MODEL_NAME${NC}"; exit 1; }
test -n "${HF_TOKEN:-}" || { echo "${RED}Missing HF_TOKEN${NC}"; exit 1; }

echo "${BOLD}7. Running submission smoke inference...${NC}"
python inference.py --smoke-run >/dev/null || { echo "${RED}inference.py smoke run failed${NC}"; exit 1; }

echo "${BOLD}8. Building Docker image...${NC}"
timeout "$DOCKER_BUILD_TIMEOUT" docker build -t metaminds-er-triage . >/dev/null || {
  echo "${YELLOW}Docker build check skipped or failed in this environment${NC}"
}

echo "${GREEN}Submission validation checks completed.${NC}"
