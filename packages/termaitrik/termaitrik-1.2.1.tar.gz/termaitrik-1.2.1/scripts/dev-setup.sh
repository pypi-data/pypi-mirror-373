#!/usr/bin/env bash
set -euo pipefail

# Creates a .venv, installs requirements and pytest
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --upgrade pytest pytest-anyio

echo "Virtualenv .venv created and dependencies installed. Activate with: source .venv/bin/activate"
