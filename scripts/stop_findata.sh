#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8010}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

pids="$("$PYTHON_BIN" - "$PORT" <<'PY'
import subprocess
import sys

port = sys.argv[1]
output = subprocess.run(["ss", "-ltnp"], text=True, capture_output=True, check=False).stdout
for line in output.splitlines():
    if f":{port} " not in line:
        continue
    marker = "pid="
    if marker in line:
        print(line.split(marker, 1)[1].split(",", 1)[0])
PY
)"

if [ -z "$pids" ]; then
  echo "端口 ${PORT} 没有 findata 服务占用"
  exit 0
fi

for pid in $pids; do
  echo "停止端口 ${PORT} 上的进程：${pid}"
  kill "$pid"
done
