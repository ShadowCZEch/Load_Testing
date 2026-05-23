#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${PROJECT_DIR}/locust_env/bin/python"

if [ ! -x "${VENV_PYTHON}" ]; then
  echo "✗ Virtual environment not found: ${PROJECT_DIR}/locust_env"
  echo "Run first:"
  echo "  chmod +x prepare_tester_python.sh"
  echo "  ./prepare_tester_python.sh"
  exit 1
fi

cd "${PROJECT_DIR}"
exec "${VENV_PYTHON}" locust_gui.py
