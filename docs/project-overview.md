# Project Overview – Minecraft Forge 1.20.1 Server Toolkit

Этот документ отвечает на два вопроса:

1. **Как устроен и работает проект.**  
2. **Какие ключевые изменения уже реализованы.**

---

## 1. Задачи проекта

Собрать репозиторий, из которого админ сможет:

1. Поднять Forge 1.20.1 сервер одной командой (`make up`).
2. Настроить всё через `.env` и быстро переключать окружения (локально / прод).
3. Управлять сервером через Docker Compose, Makefile и RCON.
4. Разделять моды на «серверные» и «клиентские», вести документацию по ним, автоматизировать загрузку с Modrinth/CurseForge.
5. Поддерживать игроков (README + player guide + скрипт установки модов на клиент).

---

## 2. Как устроен репозиторий

| Путь                     | Что лежит / зачем                                         |
|--------------------------|-----------------------------------------------------------|
| `compose/docker-compose.yml` | Описание контейнера (itzg/minecraft-server).            |
| `docker/`                | Dockerfile + локально скачанный Forge installer.         |
| `env/`                   | `.env.example` + рабочие `.env` (локальный, прод).       |
| `mods/server`, `mods/client` | `.jar` модов, разделённые на сервер и клиент.             |
| `mods/sources/`          | JSON/TXT списки, которые используют скрипты загрузки.    |
| `docs/`                  | Основная документация (modpack, deploy-guide, player-guide, overview). |
| `git/scripts/`           | Python/Bash-утилиты: Modrinth, CurseForge, ручные скачивания, Forge installer, скрипт установки клиентских модов. |
| `Makefile`               | CLI для админа: `up`, `down`, `logs`, `clean`, `fetch-mods`, `forge-installer`. |
| `ts_mods/`               | Локальная папка для временных .jar (игнорируется git).   |

---

## 3. Основные процессы

### 3.1 Конфигурация

- **Шаблон**: `env/.env.example`.  
- **Рабочие файлы**: `env/local.env` (Dev), `env/production.env` (VPS).  
- В `.env` хранятся `SERVER_PORT`, `EULA`, `MEMORY_MIN/MAX`, `OPS`, `FORGE_VERSION`, `FORGE_INSTALLER`, `ONLINE_MODE` и т.д.  
- Память выставлена 16G/28G для прод.  
- `OPS` заполняется как список ников; для оффлайн-режима вручную создаётся `data/ops.json`.

### 3.2 Makefile

| Команда            | Описание                                                                    |
|--------------------|------------------------------------------------------------------------------|
| `make up`          | `docker compose up -d` с указанным `.env`.                                   |
| `make down`        | Останавливает контейнер.                                                     |
| `make logs`        | Показывает логи (`docker compose logs -f`).                                  |
| `make clean`       | Удаляет контейнер и volume (нужен `yes`).                                    |
| `make fetch-mods`  | Modrinth + CurseForge скрипты (если есть API-ключ).                          |
| `make forge-installer` | Скачивает Forge installer в `docker/artifacts`, чтобы запускать оффлайн. |

### 3.3 Автоматическая загрузка модов

- `git/scripts/fetch_modrinth.py` читает `mods/sources/modrinth-*.json`, тянет нужные версии и пишет логи в `mods/sources/download_log.csv`.
- `git/scripts/fetch_curseforge.py` — аналог для CurseForge (если указан `CURSEFORGE_API_KEY`).
- `git/scripts/download_mods.sh` — fallback для прямых ссылок (txt-списки).
- `git/scripts/download_forge.sh` — скачивание installer’а.
- `git/scripts/install_client_mods.sh` — копирует моды игроку (для Git Bash на Windows).

### 3.4 Документация

- `README.md` — быстрый старт, структура, основные шаги.
- `docs/deploy-linux.md` — полный чек-лист для VPS.
- `docs/player-guide.md` — для игроков (Forge + копирование `.jar`).
- `docs/modpack.md` — подробное описание модов по категориям, зависимостям.
- `docs/project-overview.md` (эта заметка) — общая картина.

---

## 4. Хронология/сделанные изменения

1. **Инициализация** — структура проекта, Makefile, docker-compose, `.env`, документация (plan + project.md).
2. **Автоматизация модов** — скрипты Modrinth/CurseForge/ручные загрузки, `mods/sources/*.json`, логирование скачиваний.
3. **Документация** — README, deploy guide, player guide, modpack guide с описанием каждого мода.
4. **Синхронизация с сервером** — работа через SSH (paramiko), загрузка модов и env, `make`-команды на VPS.
5. **Расширение модпака** — добавление `Superb Warfare`, обновление GeckoLib (4.8.1), Curios (перезагрузка .jar), обновление документации и списков.
6. **ts_mods** — вспомогательная папка для обмена `.jar`; добавлена в `.gitignore`.
7. **RCON доступ** — `docker exec forge-server rcon-cli …` для выдачи `op` без рестартов.
8. **Память/режим** — правки `.env` (16G/28G, `ONLINE_MODE=FALSE`), правка `server.properties` внутри контейнера (allow-flight).

---

## 5. Как разворачивать сейчас

1. `git clone` → `cd imba_mine_serv`.
2. `cp env/.env.example env/local.env` (или `production.env`) → заполнить поля.
3. `make forge-installer` → `make fetch-mods`.
4. `make up` (или `make ENV_FILE=env/production.env up` на VPS).
5. Следить за логами через `make logs`.
6. Игрокам отдать `docs/player-guide.md` + скрипт `bash git/scripts/install_client_mods.sh`.

На прод-сервере нужно выставить firewall (`ufw`, `firewalld`, security groups) и открыть порт 25565.

---

## 6. Текущие задачи/дальнейшие шаги

- Упростить Makefile (по просьбе заказчика) — оставить только нужные команды.
- Полная документация готова; можно добавлять кейсы/FAQ, если появятся новые сценарии.
- Мод Superb Warfare синхронизирован, но при добавлении новых .jar надо класть их в `ts_mods/new/`, чтобы серверная версия не расходилась с клиентской.

---

## 7. Поддержка

Для любых правок:

1. Размещаем .jar в `ts_mods/`.
2. Обновляем `mods/server`, `mods/sources`, `docs/modpack.md`, `mods.md`.
3. Загружаем на VPS (scp/sftp), `make down && make up`.
4. Проверяем `docker ps` и `docker compose logs`.

Если нужно экстренно дать `op` или выполнить команду — `docker exec forge-server rcon-cli <команда>`.

--- 

Документ готов служить отправной точкой для тех, кто будет дорабатывать проект дальше. 
