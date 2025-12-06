#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ENV_FILE="${1:-$REPO_ROOT/env/local.env}"
TAG="${2:-manual}"

if [ ! -f "$ENV_FILE" ]; then
  echo "[grant_ops] env file $ENV_FILE not found"
  exit 0
fi

OPS_LINE="$(grep -E '^OPS=' "$ENV_FILE" | tail -n 1 || true)"
if [ -z "$OPS_LINE" ]; then
  echo "[grant_ops] OPS variable not defined in $ENV_FILE"
  exit 0
fi

OPS_VALUE="${OPS_LINE#OPS=}"
if [ -z "$OPS_VALUE" ]; then
  echo "[grant_ops] OPS value is empty"
  exit 0
fi

if ! docker ps --format '{{.Names}}' | grep -q '^forge-server$'; then
  echo "[grant_ops] forge-server container is not running"
  exit 1
fi

IFS=',' read -ra players <<<"$OPS_VALUE"
for player in "${players[@]}"; do
  name="$(echo "$player" | tr -d '\r\n' | xargs)"
  if [ -n "$name" ]; then
    echo "[grant_ops] granting op to $name ($TAG)"
    docker exec forge-server rcon-cli op "$name" >/dev/null 2>&1 || true
  fi
done
