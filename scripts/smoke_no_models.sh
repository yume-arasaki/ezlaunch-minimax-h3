#!/usr/bin/env bash
# Fast smoke: scripts + unit tests only. Never downloads models or starts Comfy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"

echo "== pytest =="
python3 -m pytest -q

echo "== help / status =="
python3 -m ezlaunch --help >/dev/null
export EZLAUNCH_HOME="${EZLAUNCH_HOME:-/tmp/ezlaunch_smoke_home_$$}"
export EZLAUNCH_MIN_DISK_GB="${EZLAUNCH_MIN_DISK_GB:-1}"
mkdir -p "$EZLAUNCH_HOME"
python3 -m ezlaunch --status

echo "== workflows =="
python3 -m ezlaunch --workflows | grep -E 't2v|i2v|ref2v' >/dev/null

echo "== shell entry =="
bash -n scripts/EZlaunch.sh
bash -n scripts/comfy-up.sh
./scripts/EZlaunch.sh --status >/dev/null

echo "== cli cancel =="
printf 'n\n' | python3 -m ezlaunch --cli >/dev/null

echo "SMOKE_NO_MODELS_OK"
