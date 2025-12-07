# Telegram Bot Specification

## 1. Goal

Build a lightweight Telegram bot (Python + aiogram 3.x) that lets the owner administer the Minecraft Forge server without touching the shell: start/stop/restart the container, inspect logs, change `.env`, manage mods/backups, and broadcast quick notifications. The bot should expose all critical actions via inline buttons so that the user can tap instead of typing commands, while text commands remain available for power users.

## 2. Functional Requirements

1. **Auth & Roles** – only a whitelist of Telegram IDs (defined in `.env.bot` via `TELEGRAM_ADMINS`) may use the bot. No moderator role is required: either you are the owner (full access) or rejected.
2. **Server control** – `/up`, `/down`, `/restart`, `/ps`, `/logs` invoke `make`/`docker compose` inside `/root/imba_mine_serv`. Each action must provide inline buttons:
   - Main menu buttons: `🟢 Up`, `🔴 Down`, `♻️ Restart`, `📊 Status`, `📜 Logs (tail 100)`, `🧹 Clean`.
   - Confirm dangerous actions (down/restart/clean) with inline “✅ Подтвердить” + “❌ Отмена”.
3. **Status** – `/status` shows: container state (`docker compose ps`), number of players (via `rcon-cli list` or `mc-monitor status`), JVM RAM usage (parse `docker stats` / `mc-monitor`). Result displayed as text + inline buttons (`🔁 Обновить`, `⬅️ Назад`).
4. **Logs** – `/logs 100` or inline “📜 Logs” button fetches `docker compose logs -n N`. For long outputs send as a file; otherwise send as text. Provide an inline selector (`Logs 50`, `Logs 200`).
5. **OP management** – `/op nickname`, `/deop nickname`, plus shortcuts: inline buttons “Опнуть ibrass”, “Снять ibrass”. All commands go through `docker exec forge-server rcon-cli`.
6. **.env editing** – `/env get KEY`, `/env set KEY VALUE` (with inline confirmation). After a successful change offer buttons `♻️ Перезапустить` or `❌ Отмена`. Always create backups (`env/.env.bot.bak`).
7. **Mod management** – `/mods server`, `/mods client` read `docs/modpack.md` to display tables. Button “📥 Загрузить мод” allows uploading `.jar`; bot saves into `ts_mods/inbox` and reports the path. Additional inline button “📦 Список новых jar”.
8. **Backups** – `/backup now` (inline “Создать бэкап”); runs `make backup` (to be implemented). Provide a download link/path once done. Later add `/backup list`.
9. **Subscriptions** – inline toggle “🔔 Краш-алерты”, “👥 Join/Leave”. The notifier tails `logs/latest.log` (async thread) and sends messages with inline “📜 Открыть лог”.
10. **Git/Deploy** – “⬇️ Pull & Restart” button executes `git pull`, `make up`, with double confirmation.

## 3. UI & UX

- Every command that matters must have inline buttons; use reply keyboards only for global navigation (e.g., “Главное меню”, “Отмена”).
- Callback data format: `action=restart`, `action=logs:100`, `action=env_set:key`. Keep it short (<64 bytes).
- Implement a simple state machine per user for multi-step flows (`/env set`, `/mods upload`). aiogram FSM or custom dictionary is acceptable.

## 4. Architecture

```
bot/
  main.py               # aiogram entrypoint, router wiring
  config.py             # load .env.bot, parse tokens/IDs
  keyboards.py          # inline & reply builders
  handlers/
     menu.py            # /start, menu navigation
     status.py          # /status, /ps
     control.py         # up/down/restart/logs buttons
     env.py             # get/set env flows
     mods.py            # list/upload mods
     ops.py             # op/deop shortcuts
     backup.py          # backup commands
  services/
     shell.py           # async subprocess runner (make/docker)
     rcon.py            # wrapper around rcon-cli
     env_file.py        # read/write env with backup
     modpack.py         # parse docs/modpack.md
     notifier.py        # tail logs, manage subscriptions
     ssh_fallback.py    # plink/ssh fallback (see section 7)
  data/
     bot.log
     state.sqlite       # optional storage (see section 6)
  README.md             # setup instructions
```

- Bot runs on the same VPS (`/root/imba_mine_serv`) via systemd unit `/etc/systemd/system/imba-bot.service`.
- Shell commands must be async (use `asyncio.create_subprocess_shell` or `aiosubprocess`) to avoid blocking.
- Long-running tasks (log tail, notifier) run in background tasks started at startup and cancelled on shutdown.

## 5. Security & Logging

- All sensitive actions are logged into `bot/data/bot.log` with timestamp, Telegram ID, command, exit code.
- Backups: before editing `.env` or other files, create `*.bak` copies with timestamp.
- Rate limit: no more than 5 actions per user per minute for destructive commands.
- `/shell` command is disabled entirely for now. Only specific, hardcoded operations exposed via inline buttons or slash commands.
- `.env.bot` is never committed; remains in `.gitignore`.

## 6. Persistence

- By default store runtime state (subscriptions, pending confirmations) in memory.
- If persistence is needed (Bot restarts frequently), use `sqlite3` via `aiosqlite`. Keep schema minimal:
  ```
  subscriptions(user_id INTEGER PRIMARY KEY,
                crashes BOOLEAN,
                joins BOOLEAN)
  ```
- No external DB is required; if persistence is unnecessary, skip SQLite entirely.

## 7. Command Execution Layer

1. **Local shell** – primary mechanism: run `make` and `docker compose` commands directly on the VPS (bot is deployed there).
2. **Dry-run mode** – add `BOT_DRY_RUN=1` (in `.env.bot`) to log the commands instead of executing. Useful for development on laptops without Docker.
3. **Fallback SSH** – when bot runs off-host (Windows desktop) it must be able to execute commands via SSH/Plink:
   - Use `PLINK_PATH` and `SSH_HOST` from `.env.bot`.
   - For each operation, decide whether to run locally or via SSH (flag `BOT_REMOTE=1`).
   - Wrap calls so that command templates are re-used (no duplication between local/remote).

## 8. Notifications

- Create a notifier service that tails `/root/imba_mine_serv/logs/latest.log` (or uses `journalctl -fu imba-mine.service`).
- When a crash or specific regex appears, send message with inline buttons:
  - “📜 Лог (50 строк)” -> fetch latest lines.
  - “🔁 Перезапустить” -> confirm restart.
- Join/Leave events: parse `latest.log` lines containing `logged in` / `left the game`, format message `👤 <nick> вошёл`.

## 9. Deployment Requirements

1. Add `make bot-install`, `make bot-run`, `make bot-service` to root Makefile.
2. Provide `docs/bot-spec.md` (this file) and extend `docs/deploy-linux.md` with bot deployment steps.
3. Systemd unit example:
   ```
   [Unit]
   Description=Imba Telegram Bot
   After=network-online.target docker.service

   [Service]
   WorkingDirectory=/root/imba_mine_serv
   ExecStart=/root/imba_mine_serv/.venv/bin/python -m bot.main
   EnvironmentFile=/root/imba_mine_serv/env/.env.bot
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

## 10. Roadmap

| Sprint | Scope |
|--------|-------|
| 1 | Skeleton (`bot/`), `.env.bot`, `/start`, `/help`, `/status`, inline main menu. |
| 2 | `/up`, `/down`, `/restart`, `/logs`, `/ps`, inline confirmations, dry-run flag. |
| 3 | `/op`, `/deop`, `/env get/set` with buttons and backups. |
| 4 | Mods listing/upload, backup commands, notifier scaffold. |
| 5 | Subscriptions (crash, join/leave), tail-based notifications, Git/Deploy buttons. |
| 6 | Polish: README, systemd unit, ssh fallback support, error reporting, tests. |

## 11. Testing & Dry-run

- Each command handler should have unit tests for parsing and formatting (use pytest).
- Provide a `BOT_DRY_RUN=1` mode in `.env.bot`. In dry-run, the bot logs command strings without executing them and replies with “(dry-run)”.
- Manual QA checklist: start bot in dry-run on local machine, tap each inline button, verify logs.

## 12. Next Steps

1. Update repository README to mention bot capabilities and inline controls.
2. Create `bot/requirements.txt`, scaffolding files, and implement sprint 1.
3. When ready, deploy via `make bot-install`, `make bot-service`, and enable systemd service.

This specification supersedes the previous version and explicitly covers inline UI, dry-run fallback, and SSH/Plink execution paths. Use it as the checklist before writing code.
