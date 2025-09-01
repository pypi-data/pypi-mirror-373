#!/usr/bin/env bash
set -euo pipefail

# Simple coverage runner for the test suite.
# Usage: bash scripts/coverage.sh [pytest-args]

# Ensure repo root as working directory
cd "$(dirname "$0")/.."

# Provide defaults for JWT-related tests if not already set
: "${ACCESS_SECRET_KEY:=access}"
: "${REFRESH_SECRET_KEY:=refresh}"
export ACCESS_SECRET_KEY REFRESH_SECRET_KEY

echo "Running pytest with coverage…"
python -m pytest -q \
  --cov=flarchitect \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml \
  "$@"

echo
echo "Coverage reports generated:"
echo "- HTML: htmlcov/index.html"
echo "- XML:  coverage.xml"
