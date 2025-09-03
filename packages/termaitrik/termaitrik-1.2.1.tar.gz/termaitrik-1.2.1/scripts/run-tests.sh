#!/usr/bin/env bash
set -euo pipefail

if [ -f .venv/bin/activate ]; then
  # shellcheck source=/dev/null
  . .venv/bin/activate
fi

python -m pytest -q --cov=termai --cov-report=term-missing --cov-report=xml "$@"
