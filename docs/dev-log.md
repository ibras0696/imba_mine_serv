# Журнал разработки — Minecraft Forge Toolkit

Хронологические заметки по репозиторию `imba_mine_serv`: что сделано, когда и зачем.

## 2025-12-05 — Старт репозитория

- Финализированы плановые документы (`PLAN.md`, `project.md`, `docs/project-overview.md`), чтобы зафиксировать рамки и ожидания до кода.
- Создан базовый каркас Docker Compose + Makefile под Forge 1.20.1 (itzg/minecraft-server).
- Стандартизирована структура каталогов: `mods/server`, `mods/client`, `mods/sources`, `ts_mods`, плюс папки для bind-монтов `config/data/logs`.
- Добавлены вспомогательные скрипты (`git/scripts/fetch_modrinth.py`, `git/scripts/fetch_curseforge.py`, `git/scripts/download_mods.sh`) для автозагрузки модов.
- Описаны структура и гайды (`README.md`, `docs/modpack.md`, `docs/player-guide.md`, `docs/deploy-linux.md`), чтобы новичкам было проще стартовать.
- Сформирован первый systemd unit (`/etc/systemd/system/imba-mine.service`) для запуска compose-стека на Linux.

## 2025-12-06 — Укрепление эксплуатации

- Введён `git/scripts/grant_ops.sh` и привязка в Makefile, чтобы выдача OP была прозрачной и повторяемой.
- Добавлен systemd таймер/сервис (`imba-mine-restart.timer` + `git/scripts/restart_server.sh`) для `/save-all`, рестарта compose и повторной выдачи OP.
- Отказ от `OPS` внутри окружения itzg‑контейнера (падал в offline‑режиме), зафиксирован ручной сценарий.
- В Makefile добавлены SSH‑алиасы (`remote-op-ibrass`) для выдачи прав с Windows‑хоста.
- Настроен logrotate (`/etc/logrotate.d/imba-mine`) для каталога `logs`.

## 2025-12-07 — Спецификация бота

- Зафиксированы требования к Telegram‑боту в `docs/bot-spec.md`: inline‑UI, dry‑run, SSH‑fallback, идеи поиска модов, уведомления, дорожная карта спринтов.
- Синхронизирована архитектурная дока с автоматизациями (auto‑OP, таймер рестарта, logrotate).

## 2025-12-07 — Спринт 1: базовый каркас

- Создан каркас `bot/` с `main.py`, `config.py`, пакетами handlers/services и inline‑меню.
- Добавлен `bot/requirements.txt` (aiogram 3, python-dotenv) и шаблон `env/.env.bot.example`; реальный `.env.bot` исключён из git.
- Реализованы `/start`, `/help`, `/status` и заготовки inline‑кнопок; статус берётся через `docker compose ps`.
- Написаны `bot/services/shell.py` и `bot/services/status.py` с поддержкой `BOT_DRY_RUN`.
- Обновлён Makefile: `remote-op-ibrass` становится основным алиасом, авто‑OP отделён от env контейнера.

## 2025-12-07 — Спринт 2: управление сервером

- Добавлен `bot/services/control.py` для `make up/down/restart/ps` и `docker compose logs --tail N`, с dry‑run и форматированием ошибок.
- Переработаны inline‑кнопки: опасные действия требуют подтверждения, логи доступны через быстрые пресеты (50/100/200) + возврат к статусу.
- Реализован `bot/handlers/control.py` для `/up`, `/down`, `/restart`, `/ps`, `/logs` и inline‑коллбеков; опасные действия показывают подтверждение.
- Обновлён `/help`, упрощён роутинг в `bot/main.py`.
- Проверена синтаксическая валидность через `python -m compileall bot`.

## 2025-12-07 — Спринт 3: OP + ENV

- Реализованы RCON‑хелперы (`bot/services/rcon.py`) и быстрые кнопки OP для ibrass; добавлены `/op` и `/deop`.
- Добавлены утилиты работы с `.env` (`bot/services/env_file.py`) и команды `/env_get`, `/env_set` с бэкапами `.bak`.
- Расширено главное меню; обработчики menu/ops/env подключены в `bot/main.py`.
- Зафиксирован прогресс; готовность Sprint 4 зависит от связки этих сервисов с нотификатором.

## 2025-12-08 — Настройка ресурсов

- Увеличены дефолтные лимиты JVM в `.env.example`/`env/local.env` до `MEMORY_MIN=6G` / `MEMORY_MAX=31G`, применены на проде.
- Ограничен контейнер Forge до 4 CPU и 31 GB RAM через `docker-compose.yml`, чтобы Docker соблюдал лимиты.
- Добавлены Makefile‑хелперы для админки с Windows: `make remote-op PLAYER=...` и `make remote-players` через Plink.
- Пересоздан прод‑контейнер (`docker compose up -d --force-recreate`) для применения новых лимитов.

## TODO / Следующие записи

- [ ] Проверка Sprint 2: прогнать кнопки на стейдже (успех/ошибка) и зафиксировать скриншоты.
- [ ] Проверка Sprint 3: прогнать `/op`, `/deop`, `/env_get`, `/env_set` в dry‑run и прод‑режиме, проверить бэкапы.
- [ ] Sprint 4: подключить backup/restore и нотификации.
- [ ] Sprint 5: реализовать поиск и загрузку модов по `bot-spec.md`.
- [ ] Sprint 6: довести мониторинг (health‑чеки, systemd‑проверки, алерты).
