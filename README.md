# Minecraft Forge 1.20.1 Server Toolkit

Проект для админа, которому нужно быстро поднять Forge‑сервер (1.20.1) на любой машине — от Windows‑ноута до VPS на Linux. Всё управление через `make`, конфигурация в `.env`, моды качаются автоматически (Modrinth/CurseForge), а игрокам даём готовый скрипт для установки клиентских модов.

## Требования

- Docker + Docker Compose (на Windows — Docker Desktop).
- Git + Make (в составе Git for Windows уже есть `bash` и `make`).
- Python 3.10+ (нужен для скриптов Modrinth/CurseForge; на Windows используем `py`).

## Структура

| Путь               | Назначение                                                                |
|--------------------|---------------------------------------------------------------------------|
| `compose/`         | `docker-compose.yml` и связанные файлы                                   |
| `docker/`          | Dockerfile + артефакты Forge installer (`docker/artifacts`)               |
| `mods/server/`     | `.jar` серверных модов (то, что монтируется в контейнер)                  |
| `mods/client/`     | полезные клиентские моды/оптимизации                                      |
| `mods/sources/`    | JSON/TXT‑списки для автоматической загрузки модов                         |
| `git/scripts/`     | Все утилиты: загрузка модов, Forge installer, установка клиентских модов |
| `env/`             | `.env.example` + твои локальные/прод конфиги                              |
| `docs/`            | Подробная документация (`modpack.md`, `player-guide.md`, `deploy-linux.md`) |
| `data/`, `logs/`   | Мир/конфиги/логи сервера (монтируются как volume)                         |

## Быстрый старт (локально/на сервере)

```bash
git clone https://github.com/ibras0696/imba_mine_serv.git
cd imba_mine_serv

cp env/.env.example env/local.env     # или env/production.env на VPS
${EDITOR:-nano} env/local.env         # правим порт, EULA, OPS, память и т.д.

make forge-installer                  # скачиваем оффлайн Forge installer в docker/artifacts
make fetch-mods                       # тянем все моды из Modrinth (+ CurseForge если есть API-ключ)

make up                               # поднимаем контейнер
make logs                             # следим за логами
```

После каждого изменения `.env` или состава модов делай `make down && make up`.

## Настройка `.env`

1. **Шаблон** — `env/.env.example`. Его не редактируем.
2. **Рабочие файлы** — `env/local.env` (для разработки) и `env/production.env`.
3. Основные поля:
   - `SERVER_PORT` — порт, который будет опубликован наружу.
   - `MEMORY_MIN` / `MEMORY_MAX` — лимиты JVM (например `4G` и `6G`).
   - `EULA=TRUE` — обязательно, иначе сервер не стартует.
   - `SERVER_NAME`, `MAX_PLAYERS`, `DIFFICULTY`, `ONLINE_MODE`.
   - `OPS=Player1,Player2` — список опов, чтобы сразу выдать админку.
   - `FORGE_VERSION` и `FORGE_INSTALLER` — уже выставлены на 1.20.1/47.4.10. Если меняешь версию, не забудь заново запустить `make forge-installer`.
4. Не нужно указывать IP — просто открой порт в фаерволе и расскажи игрокам внешний адрес вида `ip-вашего-сервера:25565`.
5. Файл не коммитим: `.gitignore` уже закрывает все `env/*.env`.

## Автозагрузка модов

1. **Modrinth** — списки `mods/sources/modrinth-server.json` и `modrinth-client.json`.
   - `make fetch-mods` → `git/scripts/fetch_modrinth.py` подтянет последние релизы Forge 1.20.1.
   - Все загрузки логируются в `mods/sources/download_log.csv`.
2. **CurseForge** — если моды есть только там (пример: FTB Ultimine).
   - Получи `CURSEFORGE_API_KEY` на https://console.curseforge.com/.
   - Добавь значение в `.env`, запусти `make fetch-mods`; тег из `mods/sources/curseforge.json` будет скачан автоматически.
3. **Ручные ссылки** — заполняем `mods/sources/server-mods.txt` или `client-mods.txt`, затем:
   ```bash
   bash git/scripts/download_mods.sh server
   ```
4. **Forge installer** — `make forge-installer` (обёртка над `git/scripts/download_forge.sh`). Контейнер получает файл через volume `docker/artifacts -> /data/artifacts`, поэтому установка не зависит от DNS внутри контейнера.

## Makefile команды

| Команда             | Что делает                                                          |
|---------------------|---------------------------------------------------------------------|
| `make up`           | `docker compose up -d` с нужным `.env`                              |
| `make down`         | останавливает и удаляет контейнер                                   |
| `make restart`      | перезапуск                                                           |
| `make logs`         | tail логов                                                           |
| `make ps`           | статус контейнера                                                    |
| `make clean`        | удаляет контейнер + тома (`data`, `logs`) после подтверждения       |
| `make rebuild`      | пересобирает образ (после правок Dockerfile)                        |
| `make fetch-mods`   | запускает Modrinth + CurseForge загрузчики                          |
| `make forge-installer` | скачивает Forge installer в `docker/artifacts`                   |

Все команды учитывают `ENV_FILE` (по умолчанию `env/local.env`). Для прод-окружения запускай так:

```bash
make ENV_FILE=env/production.env up
```

## Подготовка клиента для игроков

1. Отправь ссылку на `docs/player-guide.md` — там пошагово описано, как установить Forge, где взять моды, как подключиться к серверу.
2. Для ленивых игроков есть скрипт:
   ```bash
   bash git/scripts/install_client_mods.sh /путь/к/.minecraft/mods
   ```
   Он копирует все `.jar` из `mods/server` и `mods/client` в указанную папку. На Windows запускать из Git Bash.

## Продакшен на Linux

1. Следуй `docs/deploy-linux.md`: настрой Docker, открой порт 25565/TCP (`ufw`/`firewalld`/security group), склонируй репозиторий.
2. Скопируй `.env`: `cp env/.env.example env/production.env`, задай реальные значения.
3. Выполни `make forge-installer`, затем `make fetch-mods`.
4. Запусти `make up ENV_FILE=env/production.env`.
5. Проверь `make logs` и подключись по внешнему IP (`minecraft.example.com:25565`).

## Отладка и типичные проблемы

- **Порт занят** — `make up` вернул `port is already allocated`. Останови старый контейнер (`docker ps`, `docker stop <id>`) или поменяй `SERVER_PORT`.
- **Forge не ставится** — убедись, что заранее скачал installer (`make forge-installer`). Теперь контейнер не ходит в интернет за установщиком, поэтому DNS-проблем не будет.
- **Краш из-за зависимостей модов** — скрипты уже подхватывают `structure_gel`, `resourcefulconfig`, `sophisticatedcore` и т.д. Если добавляешь новые моды вручную, не забудь указать их зависимости в `docs/modpack.md` и в JSON‑списках.
- **Игра не видит сервер** — проверь `make ps`, `make logs`, затем убедись, что порт реально открыт (на VPS: `sudo ufw status`, `nmap your.ip -p 25565`, canyouseeme.org).

## Чем ещё полезен репозиторий

- `docs/modpack.md` — подробное описание каждого мода, зависимости, ссылки на проекты.
- `docs/player-guide.md` — понятная инструкция для игроков (даже для тех, кто впервые ставит моды).
- `docs/deploy-linux.md` — чек-лист для деплоя на VPS/дедик с комментариями по бэкапам.
- `PLAN.md` — дорожная карта и принятые решения (можно использовать как ТЗ).

Если нужна дополнительная автоматизация (бэкапы, обновление модов по расписанию, развёртывание на отдельном сервере) — пишите, добавим отдельными спринтами.
