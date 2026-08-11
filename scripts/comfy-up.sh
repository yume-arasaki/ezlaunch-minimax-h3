#!/usr/bin/env bash
# Start ComfyUI only (after first full install). Ships t2v / i2v / ref2v workflows.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m ezlaunch --launch "$@"
