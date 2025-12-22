# Обзор проекта: Minecraft Forge 1.20.1 Toolkit

Документ фиксирует текущее состояние репозитория `imba_mine_serv`, объясняет как всё работает и что было сделано за последние спринты.

## 1. Что реализовано сейчас

- **Контейнерная сборка** на базе `itzg/minecraft-server` с пользовательским Dockerfile и compose-файлом (`docker-compose.yml`). Любой админ запускает всё одной командой `make up`.
- **Единый `.env`** (`env/.env.example`, `env/local.env`, `env/production.env`) управляет портом, EULA, объёмом памяти, онлайн-режимом, списком операторов (`OPS`) и опцией `ALLOW_FLIGHT`.
- **Разделение модов**: `mods/server` (входит в контейнер) и `mods/client` (для игроков), плюс `mods/sources` с JSON/TXT для автозагрузок, и отдельная рабочая папка `ts_mods` под свежие .jar от пользователя (в `.gitignore`).
- **Автоматическая загрузка Forge и модов** через `git/scripts/fetch_modrinth.py`, `git/scripts/fetch_curseforge.py`, `git/scripts/download_forge.sh`, `git/scripts/download_mods.sh` (можно вызывать из Makefile).
- **Makefile-CLI** для старта/остановки, логов, чистки, обновления модов и выдачи опки (`make op PLAYER=Ник`).
- **Новый мир** создан на VPS (резервная копия `data/world_backup_*` лежит рядом), разрешены полёты (`allow-flight=true`) и выданы права `ibras0696`, `ibrass`.
- **Автозапуск**: на сервере создан юнит `/etc/systemd/system/imba-mine.service`, который вызывает `make up ENV_FILE=env/production.env` при старте системы (`systemctl enable --now imba-mine.service`).
- **Документация**: README, player-guide, deploy-guide, модпак-лист и данный обзор. Спецификация Telegram-бота — в `docs/bot-spec.md`.  

## 2. Структура репозитория

| Путь | Назначение |
|------|------------|
| `docker-compose.yml` | Compose с сервисами `minecraft` и `bot`, пробросом портов и volume-ами мира/логов/модов. |
| `docker/` | Dockerfile + `artifacts/` для Forge-инсталлятора. |
| `bot/` | Telegram-бот для админ-управления сервером. |
| `env/` | Образцы и рабочие `.env`. В гит попадает только `.env.example`. |
| `mods/server`, `mods/client` | `.jar` сервера и списки/архивы для клиента. |
| `mods/sources/` | JSON/TXT со ссылками на Modrinth/CurseForge (чтобы знать откуда брали файлы). |
| `git/scripts/` | Bash/Python скрипты: загрузка Forge, модов, установка клиентских модов. |
| `data/`, `logs/` | Том с миром и логами (монтируются в контейнер). |
| `ts_mods/` | Временная папка для свежих модов от пользователя. Игнорируется гитом. |
| `docs/` | Руководства: этот обзор, deploy-linux, player-guide, modpack.md, bot-spec.md. |
| `Makefile` | Команды админа (`up/down/logs/clean/fetch-mods/forge-installer/op`). |

## 3. Как работает пайплайн администратора

1. **Клонирование и подготовка `.env`**  
   ```bash
   git clone https://github.com/ibras0696/imba_mine_serv.git
   cd imba_mine_serv
   cp env/.env.example env/local.env
   ```  
   Минимум поменять: `EULA`, `SERVER_PORT`, `MEMORY_MIN/MAX`, `SERVER_NAME`, `ONLINE_MODE`, `OPS`.

2. **Forge и моды**  
   - `make forge-installer` скачает нужный installer в `docker/artifacts`.  
   - `make fetch-mods` подтянет JSON из `mods/sources/*.json`. Если нужен CurseForge — заполнить `CURSEFORGE_API_KEY`.  
   - Для ссылок, которых нет в API, добавить URL в `mods/sources/server-mods.txt` и выполнить `bash git/scripts/download_mods.sh server`.

3. **Запуск / остановка**  
   - `make up` — старт контейнера.  
   - `make logs` — «живые» логи Forge.  
   - `make down` / `make restart` — остановить/перезапустить без потери мира.  
   - `make clean` — остановить и удалить мир(+логи), используется только для полного вайпа.

4. **Выдача прав / управление**  
   - `OPS` в `.env` подключается во время старта.  
   - Быстро выдать права без редеплоя: `make op PLAYER=Ник`. Команда выполняет `docker exec forge-server rcon-cli op ...`. Для работы требуется включённый RCON (`ENABLE_RCON=TRUE`, `RCON_PASSWORD` в `.env`).  
   - Для выключения онлайн-режима используем `ONLINE_MODE=FALSE`.  
   - Разрешение полётов задаётся переменной `ALLOW_FLIGHT` (значение также продублировано в `data/server.properties`). Если меняем вручную — нужно `make restart`, чтобы сервер перечитал `server.properties`.

5. **Обновление мира / бэкапы**  
   - На VPS мир хранится в `/root/imba_mine_serv/data/world`. Свежий вайп делали перемещением `world` → `world_backup_*`, после чего контейнер создал новый.  
   - Для регулярных бэкапов можно построить команду `tar czf backup/world-$(date).tar.gz data/world`. Логично добавить таргет в Makefile (`make backup`), если понадобится.

6. **Автозапуск на проде**  
   Сервис `/etc/systemd/system/imba-mine.service` выглядит так:  
   ```ini
   [Unit]
   Description=Imba Mine Forge server
   After=docker.service
   Requires=docker.service

   [Service]
   WorkingDirectory=/root/imba_mine_serv
   ExecStart=/usr/bin/make ENV_FILE=env/production.env up
   ExecStop=/usr/bin/make ENV_FILE=env/production.env down
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```  
   Команды управления: `sudo systemctl enable --now imba-mine.service`, `sudo systemctl status imba-mine.service`. Теперь после перезагрузки VPS сервер поднимется автоматически.

7. **Сетевые настройки**  
   - На VPS открыт TCP-порт `25565` (UFW/iptables). Клиентам достаточно подключиться к `83.147.246.160:25565`.  
   - Если порт меняется, обновляем правило firewall + переменную `SERVER_PORT` + проброс в `docker-compose`.

## 4. Инструкция для игрока

1. Установить **Minecraft Forge 1.20.1** (тот же билд, что на сервере: 47.4.10).  
2. Взять клиентские моды:  
   - Скопировать `.jar` из `mods/server` (обязательные серверные моды).  
   - Дополнительно ориентироваться на `docs/modpack.md` (там разделы «Server required», «Client optional», «Performance»).  
   - Для Windows можно открыть Git Bash и выполнить  
     ```bash
     bash git/scripts/install_client_mods.sh \"$APPDATA/.minecraft/mods\"
     ```  
     Скрипт зачистит каталог и скопирует актуальные моды из `mods/client` + `mods/server`.
3. Запустить клиент Forge и подключиться к `83.147.246.160:25565`. Если модов не хватает, клиент покажет список несовпадений.  
4. Для доступа администратора на проде ник `ibrass` уже в `ops.json`. Если нужно временно выдать другому игроку — сообщить админу, чтобы он выполнил `make op PLAYER=...`.

## 5. Дополнительные скрипты и цели Makefile

| Команда | Что делает |
|---------|------------|
| `make forge-installer` | Качает installer Forge в `docker/artifacts`. |
| `make fetch-mods` | Тянет список модов с Modrinth/CurseForge. |
| `make op PLAYER=Nick` | Выдаёт админку через rcon-cli. |
| `git/scripts/install_client_mods.sh <путь>` | Копирует клиентские моды на локальный ПК. |
| `git/scripts/download_mods.sh server|client` | Массовая загрузка ссылок из `mods/sources/*.txt`. |

## 6. Чек-лист перед запуском новой версии

1. Проверить `.env` (EULA=TRUE, ONLINE_MODE нужный, OPS содержит всех админов).  
2. Выполнить `make forge-installer` и `make fetch-mods`, убедиться, что новые `.jar` попали в `mods/server`.  
3. Просмотреть `docs/modpack.md`, чтобы версии модов совпадали с тем, что реально лежит в `mods/server`.  
4. `make up` → `make logs` и дождаться строки `Done`. Ошибки о пропавших зависимостях (structure_gel, resourcefulconfig и т.д.) решаем добавлением модов.  
5. Подключиться клиентом и проверить вход без крашей.  
6. После обновления — сделать резервную копию `data/world`.  
7. На проде проверить `systemctl status imba-mine.service` и, при необходимости, перечитать сервис `sudo systemctl daemon-reload`.

## 7. Что дальше

- **Telegram-бот** (см. `docs/bot-spec.md`): aiogram 3.x, управление `make`/Docker через SSH, уведомления о крашах, оповещения об игроках.  
- **Авто-бэкапы**: отдельный скрипт или Makefile-таргет для создания архивов мира + автоматическая загрузка в S3/Google Drive.  
- **Мониторинг**: интеграция с `mc-monitor`, Prometheus Node Exporter или хотя бы `healthcheck` в docker-compose.  
- **CI-шаблон**: линтер для Python-скриптов, автопроверка `mods/sources/*.json`.  
- **Дополнительные команды Makefile**: `make backup`, `make restore`, `make update-mods`, `make tail`.  

Этот документ можно прикладывать к README или ссылаться на него в GitHub, чтобы любой админ понимал, как собрана инфраструктура и что уже настроено на проде.
