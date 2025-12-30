#!/usr/bin/env bash
set -u

SERVICE_NAME="${SERVICE_NAME:-forge-server}"

rcon() {
  docker exec "$SERVICE_NAME" rcon-cli "$@"
}

say() {
  rcon "say $*" >/dev/null 2>&1 || return 1
}

cleanup_items() {
  rcon "kill @e[type=item]" >/dev/null 2>&1 || return 1
}

sleep_and_warn() {
  local seconds="$1"
  shift
  sleep "$seconds"
  say "$*" || true
}

while true; do
  sleep_and_warn 1800 "Очистка предметов через 30 минут."
  sleep_and_warn 600 "Очистка предметов через 20 минут."
  sleep_and_warn 600 "Очистка предметов через 10 минут."
  sleep_and_warn 300 "Очистка предметов через 5 минут."
  sleep_and_warn 240 "Очистка предметов через 1 минуту."
  sleep_and_warn 30 "Очистка предметов через 30 секунд."
  sleep 25
  for i in 5 4 3 2 1; do
    say "Очистка через $i..." || true
    sleep 1
  done
  cleanup_items || true
  say "Очистка завершена." || true
done
