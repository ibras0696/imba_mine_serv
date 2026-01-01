# Minecraft Forge 1.20.1 Server Toolkit

Набор для поднятия Forge-серверов с модами и Telegram-ботом управления. В репозитории уже есть авто-скачивание модов, шаблоны env, удобный Makefile и базовые скрипты для обслуживания.

## Быстрый старт

Требования:
- Docker + Docker Compose (на Windows — Docker Desktop).
- Git + Make (на Windows удобнее через Git Bash).
- Python 3.10+ (нужен только для авто-скачивания модов).

Шаги:
1) `cp env/.env.example env/local.env` и заполни значения (EULA, порты, память).
2) `cp env/.env.bot.example .env.bot` и заполни BOT_TOKEN + TELEGRAM_ADMINS.
3) `make forge-installer`
4) `make fetch-mods`
5) `make up` (основной сервер + бот), `make up-all` (все сервера + бот) или `make up-bot` (только бот).

## Три сервера

В проекте три сервера:
- **main**: Forge + моды, порт `SERVER_PORT` (по умолчанию 25565)
- **shooter**: Forge + моды, порт `SHOOTER_SERVER_PORT` (по умолчанию 25566)
- **vanilla**: без модов, порт `VANILLA_SERVER_PORT` (по умолчанию 25567)

Данные разделены:
- `data/main` - миры и конфиги основного сервера
- `data/shooter` - миры и конфиги второго сервера
- `data/vanilla` - миры ванильного сервера
- `mods/server` - общие серверные моды

Если раньше был один мир в `data/world`, перенеси его в `data/main/world` и обнови `LEVEL_NAME`, если нужно.

Каталог `config` общий для обоих серверов. Если нужна раздельная настройка модов, сделай два каталога и обнови compose.

Переключение миров работает через `LEVEL_NAME`, `SHOOTER_LEVEL_NAME`, `VANILLA_LEVEL_NAME`.

## Управление через бота

Бот поддерживает:
- запуск/остановку/перезапуск сервера;
- статус контейнеров и логи;
- просмотр и правку env;
- список модов с ссылками;
- выбор сервера (main/shooter/vanilla);
- управление мирами (список, переключение, новый мир, загрузка ZIP/URL, бэкапы).

## Makefile команды (основные)

- `make up` - поднять основной сервер + бот
- `make up-all` - поднять все сервера + бот
- `make up-one SERVER=shooter` - поднять только один сервер
- `make up-bot` - поднять только бота
- `make logs SERVER=shooter` - логи выбранного сервера
- `make clean-data` - удалить `data/main`, `data/shooter`, `data/vanilla` (опасно)

## Документация

docs/
├─ [project-overview.md](docs/project-overview.md) - обзор проекта и структуры
├─ [system-architecture.md](docs/system-architecture.md) - архитектура контейнеров и данных
├─ [deploy-linux.md](docs/deploy-linux.md) - установка на Linux/VPS + systemd
├─ [player-guide.md](docs/player-guide.md) - инструкция для игроков
├─ [modpack.md](docs/modpack.md) - описание сборки и источников модов
├─ [download-links.md](docs/download-links.md) - где обновлять списки модов
├─ [bot-spec.md](docs/bot-spec.md) - возможности Telegram-бота
├─ [dev-log.md](docs/dev-log.md) - краткий журнал изменений
└─ tz/
   └─ [servers-bot-worlds.md](docs/tz/servers-bot-worlds.md) - ТЗ по ботам/мирам

Также:
- [mods.md](mods.md) — список модов и ссылки

## Полезные файлы

- `env/.env.example` — шаблон env
- `env/.env.bot.example` — шаблон env для бота
- `mods/sources/` — списки модов (Modrinth/CurseForge/прямые ссылки)
- `git/scripts/` — скрипты для скачивания модов и установки
