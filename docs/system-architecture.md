# Архитектура

## Контейнеры

- `minecraft` (main) - основной сервер Forge
- `minecraft_shooter` - второй сервер Forge
- `minecraft_vanilla` - ванильный сервер без модов
- `bot` - Telegram-бот управления

## Данные и тома

- `data/main` - данные основного сервера (`/data` внутри контейнера)
- `data/shooter` - данные второго сервера (`/data` внутри контейнера)
- `data/vanilla` - данные ванильного сервера (`/data` внутри контейнера)
- `config` - общий каталог конфигов модов (`/data/config`)
- `mods/server` - общие серверные моды (`/data/mods`)
- `docker/artifacts` - Forge installer (`/data/artifacts`)

## Порты

- main: `SERVER_PORT` (по умолчанию 25565)
- shooter: `SHOOTER_SERVER_PORT` (по умолчанию 25566)
- vanilla: `VANILLA_SERVER_PORT` (по умолчанию 25567)

## Конфигурация

Используется один env-файл (`env/production.env` или `env/local.env`) с тремя наборами переменных:
- основной сервер: `LEVEL_NAME`, `MEMORY_MIN`, `ONLINE_MODE`, и т.д.
- shooter сервер: `SHOOTER_LEVEL_NAME`, `SHOOTER_MEMORY_MIN`, `SHOOTER_ONLINE_MODE`, и т.д.
- vanilla сервер: `VANILLA_LEVEL_NAME`, `VANILLA_MEMORY_MIN`, `VANILLA_ONLINE_MODE`, и т.д.

## Бот

Бот читает `.env.bot` и работает через Docker socket:
- управление контейнерами (start/stop/restart/logs)
- просмотр/правка env
- управление мирами и бэкапами
- выбор сервера (main/shooter/vanilla)
