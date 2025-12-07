# Системная логика и текущая функциональность

Документ описывает, как устроена инфраструктура сборки `imba_mine_serv`: какие сервисы участвуют, как они взаимодействуют, и какие автоматизации уже внедрены к текущему моменту (07.12.2025). Используйте этот файл как ориентир при разработке и отладке.

## 1. Общая схема

```
├── Docker Compose (compose/docker-compose.yml)
│     └── forge-server (itzg/minecraft-server + кастомный Dockerfile)
│           ├─ /data/world        (bind: ./data/world)
│           ├─ /data/config       (bind: ./config)
│           ├─ /data/mods         (bind: ./mods/server)
│           ├─ /data/logs         (bind: ./logs)
│           ├─ /data/artifacts    (bind: ./docker/artifacts)
│           └─ RCON порт 25575
├── Makefile CLI
│     ├─ up / down / restart / logs / ps
│     ├─ forge-installer, fetch-mods
│     ├─ op (локальный), op-ibrass, remote-op-ibrass
│     └─ интеграция с grant_ops.sh
├── systemd службы
│     ├─ imba-mine.service        (поднимает docker compose)
│     ├─ imba-mine-restart.service (save-all + restart + grant ops)
│     └─ imba-mine-restart.timer  (каждые 3 часа)
└── Скрипты автозагрузки
      ├─ git/scripts/grant_ops.sh
      └─ git/scripts/restart_server.sh
```

## 2. Docker Compose

- Единственный сервис `minecraft` собирается из `docker/Dockerfile` и запускает Forge 1.20.1 (Java 17).  
- Переменные окружения читаются из `.env` (по умолчанию `env/local.env`, на проде `env/production.env`).  
- После удаления переменной `OPS` из compose-файла контейнер больше не пытается самостоятельно управлять операторами (это было причиной падений в offline-режиме).  
- Все данные мира, логов, конфигов, модов находятся на хосте (каталоги `data/`, `logs/`, `config/`, `mods/server/`, `docker/artifacts/`).

## 3. Makefile

### Базовые команды
| Команда | Описание |
|---------|----------|
| `make up` | Проверяет наличие `.env`, выполняет `docker compose up -d`, затем вызывает `grant_ops.sh` (автовыдача OP). |
| `make down` | Останавливает контейнер и оставляет тома. |
| `make restart` | Последовательно `down` + `up`. |
| `make logs` | `docker compose logs -f` (стрим логов сервера). |
| `make ps` | Показывает состояние контейнера. |
| `make clean` | Останавливает и удаляет контейнер + тома (мир/логи) с подтверждением. |
| `make fetch-mods` | Загружает моды из `mods/sources/*.json` (Modrinth + CurseForge). |
| `make forge-installer` | Скачивает инсталлятор Forge в `docker/artifacts`. |

### OP-команды
- `make op PLAYER=имя` — локальный `docker exec forge-server rcon-cli op ...`.
- `make op-ibrass` — алиас для локального `op`.
- `make remote-op-ibrass SSH_PASSWORD=...` — через `tools/plink.exe` подключается по SSH и выполняет `rcon-cli op ibrass`. Полезно на Windows без Docker.

### Авто-OP
- После `make up` автоматически запускается `bash git/scripts/grant_ops.sh`, который читает `OPS=` из заданного `.env`, проверяет, что контейнер работает, и выдаёт оператора каждому нику (через `rcon-cli`). Если список пуст, скрипт ничего не делает.

## 4. Система перезапусков

### Скрипт `git/scripts/restart_server.sh`
1. Определяет корень репозитория, `.env` и compose-файл.
2. Если контейнер запущен:
   - Отсчитывает 15 секунд (каждую секунду отправляется сообщение `[auto-restart] Перезапуск через N сек`).
   - Отправляет сообщение о сохранении мира, выполняет `save-all flush`.
3. Выполняет `docker compose restart`.
4. Снова вызывает `grant_ops.sh`, чтобы вернуть оператора всем из `.env`.

### systemd unit & timer
- `/etc/systemd/system/imba-mine-restart.service` запускает скрипт и пост-командой повторно выдаёт op (`docker exec ... op ibras0696` и `op ibrass` — для гарантии).
- `/etc/systemd/system/imba-mine-restart.timer` запланирован каждые 3 часа (`OnBootSec=3h`, `OnUnitActiveSec=3h`).  
- `systemctl list-timers imba-mine-restart.timer` показывает следующий запуск.

## 5. Grant OPS

`git/scripts/grant_ops.sh`:
- Аргументы: путь к `.env` (по умолчанию `env/local.env`), тег (например, `make-up`, `auto-restart`).
- Читает `OPS=` (последнюю строку, если их несколько) и парсит список через запятую.
- Если контейнер `forge-server` в состоянии `Up`, вызывает `docker exec ... rcon-cli op <ник>` для каждого.
- Используется:
  - `make up` ⇒ автоматически.
  - `restart_server.sh` ⇒ после каждого планового рестарта.
  - Администратором вручную: `bash git/scripts/grant_ops.sh env/production.env manual`.

## 6. Logrotate

- Конфиг `/etc/logrotate.d/imba-mine` обслуживает `logs/*.log`.
- Параметры: `daily`, `rotate 7`, `compress`, `delaycompress`, `copytruncate`.
- Это позволяет держать размер каталога под контролем, не мешая работе контейнера (используется `copytruncate`).

## 7. Документы и процессы

- `docs/project-overview.md` — высокоуровневое описание цели проекта, структуры каталога и сценариев админа.
- `docs/dev-log.md` — хронология выполненных работ (обновляется после каждой итерации).
- `docs/bot-spec.md` — спецификация будущего Telegram-бота (inline-buttons, dry-run, SSH fallback, мод-парсер, подписки).
- `docs/player-guide.md` — инструкция для игроков (установка модов, подключение).
- `docs/deploy-linux.md` — шаги деплоя на новом сервере (Docker, системные службы, firewall).

## 8. Текущие проблемы и решения

1. **Offline ники и итерация “manage-users”**: если в `.env` указать `OPS=ibrass`, itzg-образ будет пытаться искать ник через Playerdb и падать. Поэтому `OPS` в `env/production.env` оставлен пустым, а выдача прав перенесена в `grant_ops.sh`.
2. **SSH на Windows**: для команд типа `op ibrass` без Docker добавлена `remote-op-ibrass` с Plink (`tools/plink.exe`).
3. **Память сервера**: таймер перезапуска каждые 3 часа, `save-all` перед рестартом, logrotate для логов.

## 9. Next steps (в контексте существующей логики)

- Начать реализацию Telegram-бота по спринтам (см. `docs/bot-spec.md`).
- Добавить `make backup`/`make restore` для мира и интеграцию с ботом.
- Реализовать автоматическую запись изменений `env/production.env` (например, через `git/hooks` + копию на сервере).
- Рассмотреть мониторинг (`mc-monitor` / Prometheus) и алармы в Telegram.

Следите за обновлениями в `docs/dev-log.md` и расширяйте этот документ, когда инфраструктура изменяется.
