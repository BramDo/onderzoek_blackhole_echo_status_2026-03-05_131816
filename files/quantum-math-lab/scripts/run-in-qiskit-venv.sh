#!/usr/bin/env bash
set -euo pipefail

# Minimal launcher used throughout the repo docs.
# Default venv matches the current project convention but can be overridden.

QISKIT_VENV="${QISKIT_VENV:-/home/bram/.venvs/qiskit}"
PYTHON_BIN="${QISKIT_VENV}/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python not found in Qiskit venv: $PYTHON_BIN" >&2
  echo "Set QISKIT_VENV to the correct virtualenv root." >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "Usage: scripts/run-in-qiskit-venv.sh <command> [args...]" >&2
  exit 2
fi

if [[ "$1" == "python" ]]; then
  shift
fi

exec "$PYTHON_BIN" "$@"
