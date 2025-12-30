#!/usr/bin/env bash
# Устанавливает клиентские моды в указанную папку .minecraft/mods

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODS_SERVER_DIR="${ROOT_DIR}/mods/server"
MODS_CLIENT_DIR="${ROOT_DIR}/mods/client"
DEST_DIR="${1:-$HOME/.minecraft/mods}"

if [[ -z "${DEST_DIR}" ]]; then
  echo "Нужно указать путь до .minecraft/mods."
  echo "Пример: bash git/scripts/install_client_mods.sh /path/to/.minecraft/mods"
  exit 1
fi

echo "Целевая папка: ${DEST_DIR}"
mkdir -p "${DEST_DIR}"

if [[ -f "${ROOT_DIR}/env/local.env" ]]; then
  set -a
  . "${ROOT_DIR}/env/local.env"
  set +a
fi

echo "[1/3] Обновляю список модов (make fetch-mods)..."
(cd "${ROOT_DIR}" && make fetch-mods)

echo "[2/3] Копирую серверные моды из mods/server..."
find "${MODS_SERVER_DIR}" -maxdepth 1 -name '*.jar' -print -exec cp {} "${DEST_DIR}/" \;

echo "[3/3] Копирую клиентские моды из mods/client..."
find "${MODS_CLIENT_DIR}" -maxdepth 1 -name '*.jar' -print -exec cp {} "${DEST_DIR}/" \;

echo "Готово. Запусти Forge 1.20.1 и подключайся к серверу."
