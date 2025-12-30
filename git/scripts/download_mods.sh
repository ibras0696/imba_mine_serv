#!/usr/bin/env bash
# Скачивает моды по спискам в mods/sources/*.txt.
# Формат строки: https://example.com/file.jar OptionalName.jar

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_DIR="${ROOT_DIR}/mods/sources"
SERVER_LIST="${SRC_DIR}/server-mods.txt"
CLIENT_LIST="${SRC_DIR}/client-mods.txt"

DEST_SERVER="${ROOT_DIR}/mods/server"
DEST_CLIENT="${ROOT_DIR}/mods/client"

TARGET="${1:-all}"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Каталог со списками не найден: $SRC_DIR"
  exit 1
fi

if command -v curl >/dev/null 2>&1; then
  DL_CMD="curl"
elif command -v wget >/dev/null 2>&1; then
  DL_CMD="wget"
else
  echo "Не найден curl или wget. Установи один из них."
  exit 1
fi

download_file() {
  local url="$1"
  local dest="$2"
  local tmp
  tmp="$(mktemp)"

  echo "Скачиваю: $url -> $dest"
  if [[ "$DL_CMD" == "curl" ]]; then
    curl -fSL "$url" -o "$tmp"
  else
    wget -q -O "$tmp" "$url"
  fi

  mv "$tmp" "$dest"
  echo "Готово: $dest"
}

process_list() {
  local list_file="$1"
  local dest_dir="$2"

  if [[ ! -f "$list_file" ]]; then
    echo "Список не найден: $list_file"
    return
  fi

  mkdir -p "$dest_dir"

  while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    local line
    line="$(sed 's/#.*$//' <<<"$raw_line" | xargs || true)"
    [[ -z "$line" ]] && continue

    local url filename
    read -r url filename <<<"$line"
    [[ -z "$url" ]] && continue

    if [[ -z "${filename:-}" ]]; then
      filename="$(basename "$url")"
    fi

    local dest_path="${dest_dir}/${filename}"
    if [[ -f "$dest_path" ]]; then
      echo "Уже есть: $dest_path"
      continue
    fi

    download_file "$url" "$dest_path"
  done <"$list_file"
}

case "$TARGET" in
  server)
    process_list "$SERVER_LIST" "$DEST_SERVER"
    ;;
  client)
    process_list "$CLIENT_LIST" "$DEST_CLIENT"
    ;;
  all)
    process_list "$SERVER_LIST" "$DEST_SERVER"
    process_list "$CLIENT_LIST" "$DEST_CLIENT"
    ;;
  *)
    echo "Использование: $0 [all|server|client]"
    exit 1
    ;;
esac

echo "Готово."
