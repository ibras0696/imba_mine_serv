#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

ENV_FILE="${1:-$REPO_ROOT/env/production.env}"
COMPOSE_FILE="$REPO_ROOT/docker-compose.yml"

cd "$REPO_ROOT"

if docker ps --format '{{.Names}}' | grep -q '^forge-server$'; then
  for sec in $(seq 15 -1 1); do
    docker exec forge-server rcon-cli say "[auto-restart] Перезапуск через ${sec} сек" >/dev/null 2>&1 || true
    sleep 1
  done
  docker exec forge-server rcon-cli say "[auto-restart] Saving world before restart..." >/dev/null 2>&1 || true
  docker exec forge-server rcon-cli save-all flush >/dev/null 2>&1 || true
  sleep 2
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" restart

bash "$SCRIPT_DIR/grant_ops.sh" "$ENV_FILE" "auto-restart" || true
