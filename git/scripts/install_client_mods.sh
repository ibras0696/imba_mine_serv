#!/usr/bin/env bash
# Скрипт для игрока: скачивает и копирует клиентские моды в локальный .minecraft/mods

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODS_SERVER_DIR="${ROOT_DIR}/mods/server"
MODS_CLIENT_DIR="${ROOT_DIR}/mods/client"
SOURCES_DIR="${ROOT_DIR}/mods/sources"
DEST_DIR="${1:-$HOME/.minecraft/mods}"

if [[ -z "${DEST_DIR}" ]]; then
  echo "Не указана папка назначения. Пример:"
  echo "  bash git/scripts/install_client_mods.sh /path/to/.minecraft/mods"
  exit 1
fi

echo "Целевая папка: ${DEST_DIR}"
mkdir -p "${DEST_DIR}"

# 1. Скачиваем свежие моды (Modrinth + CurseForge, если есть ключ)
if [[ -f "${ROOT_DIR}/env/local.env" ]]; then
  set -a
  . "${ROOT_DIR}/env/local.env"
  set +a
fi

echo "[1/3] Скачиваем моды через make fetch-mods (может потребоваться CURSEFORGE_API_KEY)"
(cd "${ROOT_DIR}" && make fetch-mods)

# 2. Копируем обязательные .jar (server + client) в целевую папку
echo "[2/3] Копируем моды из mods/server..."
find "${MODS_SERVER_DIR}" -maxdepth 1 -name '*.jar' -print -exec cp {} "${DEST_DIR}/" \;

echo "[3/3] Копируем моды из mods/client..."
find "${MODS_CLIENT_DIR}" -maxdepth 1 -name '*.jar' -print -exec cp {} "${DEST_DIR}/" \;

echo "Готово! Запускай Forge 1.20.1 и подключайся к серверу."
