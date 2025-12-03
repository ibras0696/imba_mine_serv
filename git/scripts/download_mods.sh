#!/usr/bin/env bash
# Скрипт для автоматической загрузки модов в папки mods/server и mods/client.
# Использует списки URL'ов из mods/sources/*.txt. Формат файла:
#   https://example.com/file.jar CustomName.jar
# Второй столбец (имя файла) опционален — если его нет, берём basename из URL.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_DIR="${ROOT_DIR}/mods/sources"
SERVER_LIST="${SRC_DIR}/server-mods.txt"
CLIENT_LIST="${SRC_DIR}/client-mods.txt"

DEST_SERVER="${ROOT_DIR}/mods/server"
DEST_CLIENT="${ROOT_DIR}/mods/client"

TARGET="${1:-all}"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "❌ Не найдена папка с источниками модов: $SRC_DIR"
  exit 1
fi

if command -v curl >/dev/null 2>&1; then
  DL_CMD="curl"
elif command -v wget >/dev/null 2>&1; then
  DL_CMD="wget"
else
  echo "❌ Установите curl или wget для работы скрипта."
  exit 1
fi

download_file() {
  local url="$1"
  local dest="$2"
  local tmp
  tmp="$(mktemp)"

  echo "⬇️  Скачиваю $url → $dest"
  if [[ "$DL_CMD" == "curl" ]]; then
    curl -fSL "$url" -o "$tmp"
  else
    wget -q -O "$tmp" "$url"
  fi

  mv "$tmp" "$dest"
  echo "✅ Готово: $dest"
}

process_list() {
  local category="$1"
  local list_file="$2"
  local dest_dir="$3"

  if [[ ! -f "$list_file" ]]; then
    echo "ℹ️  Список $list_file не найден — пропускаю."
    return
  fi

  mkdir -p "$dest_dir"

  while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    # Удаляем комментарии и пробелы по краям
    local line
    line="$(sed 's/#.*$//' <<<"$raw_line" | xargs || true)"
    [[ -z "$line" ]] && continue

    local url filename
    read -r url filename <<<"$line"
    if [[ -z "$url" ]]; then
      continue
    fi

    if [[ -z "${filename:-}" ]]; then
      filename="$(basename "$url")"
    fi

    local dest_path="${dest_dir}/${filename}"
    if [[ -f "$dest_path" ]]; then
      echo "⏭  Уже скачан: $dest_path"
      continue
    fi

    download_file "$url" "$dest_path"
  done <"$list_file"
}

case "$TARGET" in
  server)
    process_list "server" "$SERVER_LIST" "$DEST_SERVER"
    ;;
  client)
    process_list "client" "$CLIENT_LIST" "$DEST_CLIENT"
    ;;
  all)
    process_list "server" "$SERVER_LIST" "$DEST_SERVER"
    process_list "client" "$CLIENT_LIST" "$DEST_CLIENT"
    ;;
  *)
    echo "Usage: $0 [all|server|client]"
    exit 1
    ;;
esac

echo "🎉 Загрузка завершена."
