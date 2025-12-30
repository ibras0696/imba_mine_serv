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
make up-all       # оба сервера + бот
```

## 7. Systemd (автостарт)

### Основной сервер + бот

`/etc/systemd/system/new-sborka-hard.service`:

```ini
[Unit]
Description=New Sborka Hard (main + bot)
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/root/new_sborka_hard
ExecStart=/usr/bin/make ENV_FILE=env/production.env up
ExecStop=/usr/bin/make ENV_FILE=env/production.env down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Второй сервер (shooter)

`/etc/systemd/system/new-sborka-hard-shooter.service`:

```ini
[Unit]
Description=New Sborka Hard (shooter)
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/root/new_sborka_hard
ExecStart=/usr/bin/make ENV_FILE=env/production.env up-one SERVER=shooter
ExecStop=/usr/bin/make ENV_FILE=env/production.env stop SERVER=shooter
Restart=on-failure

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
sudo systemctl enable --now new-sborka-hard-cleanup.service
```

## 8. Firewall

Открой TCP порты:
- 25565 (main)
- 25566 (shooter)
