#!/bin/bash
#SBATCH -J purpletrader-bots
#SBATCH -o purpletrader-bots.%j.out
#SBATCH -e purpletrader-bots.%j.err
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 4
#SBATCH --time=04:00:00

set -euo pipefail

ENGINE_URL="http://live.acquantclub.com"
PYTHON_BIN="python3"

cleanup() {
  echo "Cleaning up at $(date)"
  pkill -P $$ 2>/dev/null || true
}
trap cleanup EXIT

wait_for_health() {
  local url="$1"
  local timeout="${2:-60}"
  local start_ts now
  start_ts=$(date +%s)
  echo "Waiting for engine health at ${url} (timeout ${timeout}s)"
  until curl -fsS "${url}" >/dev/null 2>&1; do
    sleep 1
    now=$(date +%s)
    if (( now - start_ts > timeout )); then
      echo "Engine health check timed out after ${timeout}s" >&2
      return 1
    fi
  done
  echo "Engine is healthy."
}

echo "Starting bots on $(hostname) at $(date)"

# Ensure remote engine is reachable before starting bots
wait_for_health "${ENGINE_URL}/health" 90 || {
  echo "Remote engine failed health check; exiting" >&2
  exit 1
}

${PYTHON_BIN} -m bots.runner --base-url "$ENGINE_URL" --config "$(dirname "$0")/bots.yaml" &

wait


