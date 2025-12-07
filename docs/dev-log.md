# Development Log – Minecraft Forge Toolkit

Этот файл фиксирует все этапы работы в репозитории `imba_mine_serv`. После каждого спринта или крупной задачи сюда добавляется запись с кратким описанием, датой и ссылками на связанные файлы/коммиты.

## 2025-12-05 — Базовая инфраструктура

- Описаны требования и структура проекта (`PLAN.md`, `project.md` → `docs/project-overview.md`).
- Настроен Docker Compose + Makefile для сервера Forge 1.20.1.
- Созданы каталоги `mods/server`, `mods/client`, `mods/sources`, `ts_mods`.
- Добавлены скрипты авто-загрузки Forge и модов (`git/scripts/fetch_modrinth.py`, `…/fetch_curseforge.py`, `…/download_mods.sh`).
- Документация: `README.md`, `docs/modpack.md`, `docs/player-guide.md`, `docs/deploy-linux.md`.
- Автозапуск сервера через systemd (`/etc/systemd/system/imba-mine.service`).

## 2025-12-06 — Автоматизация прав и перезапуска

- Добавлен `git/scripts/grant_ops.sh` и интеграция в Makefile (`make up` → автоматическая выдача OP из `.env`).
- Создан systemd-таймер `imba-mine-restart.timer`, скрипт `git/scripts/restart_server.sh` (save-all + restart + grant ops).
- В `.env` и compose-файле удалена интеграция с `OPS` из itzg-image (приводила к падению при оффлайн никах).
- Добавлены `remote-op-ibrass` и локальные alias команды в Makefile.
- Настроен logrotate (`/etc/logrotate.d/imba-mine`) для `logs/*.log`.

## 2025-12-07 — Bot Specification и будущие фичи

- `docs/bot-spec.md`: ТЗ на Telegram-бота (inline UI, dry-run, SSH fallback, мод-парсер, подписки).
- Roadmap по спринтам 1–6 для бота.

## TODO / Next Entries

- [ ] Спринт 1 бота: scaffold `bot/`, `.env.bot`, `/start`, `/help`, `/status`, inline меню.
- [ ] Спринт 2: управление сервером (`/up`, `/down`, `/restart`, `/logs`, `/ps`).
- [ ] Спринт 3: OP/ENV команды.
- [ ] Спринт 4: мод-парсер и backups.
- [ ] Спринт 5: подписки и уведомления.
- [ ] Спринт 6: релиз, systemd сервис, тесты.

При добавлении новых задач обновляйте этот log, чтобы всегда видеть историю изменений и прогресс по спринтам.
