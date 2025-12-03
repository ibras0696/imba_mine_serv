#!/usr/bin/env bash
# Скачивает оф. Forge installer через curl/wget.
# Использование:
#   ./git/scripts/download_forge.sh [MC_VERSION] [FORGE_BUILD]
# Пример: ./git/scripts/download_forge.sh 1.20.1 47.2.0

set -euo pipefail

MC_VERSION="${1:-1.20.1}"
FORGE_BUILD="${2:-47.2.0}"

FORGE_ID="${MC_VERSION}-${FORGE_BUILD}"
FORGE_FILENAME="forge-${FORGE_ID}-installer.jar"
URL="https://maven.minecraftforge.net/net/minecraftforge/forge/${FORGE_ID}/${FORGE_FILENAME}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEST_DIR="${ROOT_DIR}/docker/artifacts"
DEST_FILE="${DEST_DIR}/${FORGE_FILENAME}"

mkdir -p "$DEST_DIR"

if command -v curl >/dev/null 2>&1; then
  DL_CMD="curl"
elif command -v wget >/dev/null 2>&1; then
  DL_CMD="wget"
else
  echo "❌ Установите curl или wget для работы скрипта."
  exit 1
fi

if [[ -f "$DEST_FILE" ]]; then
  echo "⏭  Forge уже скачан: $DEST_FILE"
  exit 0
fi

echo "⬇️  Скачиваю Forge ${FORGE_ID}"
if [[ "$DL_CMD" == "curl" ]]; then
  curl -fSL "$URL" -o "$DEST_FILE"
else
  wget -q -O "$DEST_FILE" "$URL"
fi

echo "✅ Готово: $DEST_FILE"
echo "Помести этот installer рядом с Dockerfile, если решишь собирать собственный образ без itzg/minecraft-server."
