#!/usr/bin/env bash
# Double-click / run from terminal — Linux entrypoint
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install python3 then try again."
  read -r -p "Press Enter to close…"
  exit 1
fi

# Run from the repo tree without requiring a system-wide install
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Minimal launcher deps (user install — no admin)
python3 -m pip install --user -q pyyaml "huggingface_hub>=0.23" requests 2>/dev/null || true

exec python3 -m ezlaunch "$@"
