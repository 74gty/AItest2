#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
HOST="${2:-127.0.0.1}"

cd "$(dirname "$0")/.."
./.venv/bin/python -m uvicorn findata_service.app:app --host "$HOST" --port "$PORT"
