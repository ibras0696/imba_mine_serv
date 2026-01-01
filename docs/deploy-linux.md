# Деплой на Linux/VPS

## 1. Установка зависимостей

- Docker + Docker Compose
- Git
- Make (опционально, но удобно)

## 2. Клонирование

```bash
git clone https://github.com/ibras0696/imba_mine_serv.git
cd imba_mine_serv
```

## 3. Конфигурация env

```bash
cp env/.env.example env/production.env
nano env/production.env
```

Проверь:
- `EULA=TRUE`
- `ONLINE_MODE=FALSE` (если нужен оффлайн режим)
- порты `SERVER_PORT` и `SHOOTER_SERVER_PORT`
- память `MEMORY_MIN/MAX` и `SHOOTER_MEMORY_MIN/MAX`

## 4. Telegram-бот

```bash
cp env/.env.bot.example .env.bot
nano .env.bot
```

Заполни:
- `BOT_TOKEN`
- `TELEGRAM_ADMINS`
- `WORKDIR` (путь к репозиторию)

## 5. Скачивание модов и Forge

```bash
make forge-installer
make fetch-mods
```

## 6. Запуск

```bash
make up           # основной сервер + бот
make up-all       # все сервера + бот
```

## 7. Systemd (автостарт)

### Только бот (рекомендуется)

Скопируй файл:

```bash
sudo cp deploy/systemd/new-sborka-hard.service /etc/systemd/system/new-sborka-hard.service
```

Содержимое `/etc/systemd/system/new-sborka-hard.service`:

```ini
[Unit]
Description=New Sborka Hard (bot only)
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/root/new_sborka_hard
Environment=ENV_FILE=env/production.env
ExecStart=/usr/bin/make up-bot
ExecStop=/usr/bin/make stop-bot

[Install]
WantedBy=multi-user.target
```

Серверы запускай вручную (`make up`, `make up-one SERVER=...`) или через Telegram-бота.

### Только shooter (опционально)

`/etc/systemd/system/new-sborka-hard-shooter.service`:

```ini
[Unit]
Description=New Sborka Hard (shooter)
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/root/new_sborka_hard
Environment=ENV_FILE=env/production.env
ExecStart=/usr/bin/make up-one SERVER=shooter
ExecStop=/usr/bin/make stop SERVER=shooter

[Install]
WantedBy=multi-user.target
```

### Только vanilla (опционально)

`/etc/systemd/system/new-sborka-hard-vanilla.service`:

```ini
[Unit]
Description=New Sborka Hard (vanilla)
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/root/new_sborka_hard
Environment=ENV_FILE=env/production.env
ExecStart=/usr/bin/make up-one SERVER=vanilla
ExecStop=/usr/bin/make stop SERVER=vanilla

[Install]
WantedBy=multi-user.target
```

### Очистка предметов

Используй сервисы из `deploy/systemd/`:
- `new-sborka-hard-cleanup.service`
- `new-sborka-hard-cleanup-shooter.service`

Активировать:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now new-sborka-hard.service
sudo systemctl enable --now new-sborka-hard-shooter.service # если нужен отдельный сервис
sudo systemctl enable --now new-sborka-hard-vanilla.service # если нужен отдельный сервис
sudo systemctl enable --now new-sborka-hard-cleanup.service
```

## 8. Firewall

Открой TCP порты:
- 25565 (main)
- 25566 (shooter)
- 25567 (vanilla)
