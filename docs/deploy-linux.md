# Гайд: деплой Minecraft Forge сервера на Linux (VPS)

> Этот документ рассчитан на чайника. Следуем шагам сверху вниз. Никаких Windows — только Linux (Ubuntu/Debian/RHEL и т.п.).

---

## 1. Подготовка сервера

1. Берём чистый VPS/Dedicated с публичным IPv4.
2. Заходим по SSH: `ssh user@your.ip`.
3. Обновляем систему:
   ```bash
   sudo apt update && sudo apt upgrade -y    # для Debian/Ubuntu
   ```
4. Ставим Docker + Docker Compose:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER  # чтобы не писать sudo каждый раз
   ```
   > После этого перелогинься (или `newgrp docker`), чтобы права применились.

---

## 2. Клонирование репозитория

```bash
git clone https://example.com/forge-toolkit.git
cd forge-toolkit
```

> Ссылка — любая, куда зальём этот проект. Если нет Git, ставим: `sudo apt install git -y`.

---

## 3. Настройка `.env`

1. Создаём рабочий файл: `cp env/.env.example env/production.env`.
2. Правим значения в `env/production.env`:
   - `SERVER_PORT=25565`
   - `EULA=TRUE`
   - `SERVER_NAME=My Forge Server`
   - `MEMORY_MIN/MAX` под ресурсы VPS (обычно 2G/4G минимум).
3. Для Makefile скажем использовать прод-файл: `export ENV_FILE=env/production.env` или укажем при вызове (`make up ENV_FILE=env/production.env`).

---

## 4. Проброс порта

1. Разрешаем порт в UFW:
   ```bash
   sudo ufw allow 25565/tcp
   sudo ufw reload
   ```
2. Если UFW не установлен, ставим: `sudo apt install ufw -y`.
3. Для firewalld (CentOS/RHEL):
   ```bash
   sudo firewall-cmd --add-port=25565/tcp --permanent
   sudo firewall-cmd --reload
   ```
4. Проверяем внешние security groups (AWS, GCP, Hetzner и т.д.) — порт должен быть разрешён.

---

## 5. Старт сервера

```bash
make up ENV_FILE=env/production.env
```

Полезные команды:
- `make logs ENV_FILE=env/production.env` — логи сервера.
- `make ps ENV_FILE=env/production.env` — статус контейнера.
- `make down ENV_FILE=env/production.env` — остановить.
- `make clean ENV_FILE=env/production.env` — снести вместе с томами (осторожно, удалит мир).

---

## 6. Проверка доступности

1. С другого устройства запускаем Minecraft Forge 1.20.1, добавляем сервер `your.ip:25565`.
2. Если не заходит — проверяем:
   - `make logs` на ошибки модов/EULA.
   - `sudo ufw status` / `firewall-cmd --list-ports`.
   - `curl https://canyouseeme.org` → тестируем порт.

---

## 7. Обновления и бэкапы

1. Прежде чем обновлять моды/Forge:
   - `make down`
   - делаем бэкап папки `data/world` и `config`.
2. Заливаем новые `.jar` в `mods/server`, обновляем `docs/modpack.md`.
3. `make up` — сервер поднимется с новыми модами.

---

## 8. Автоматизация (опционально)

- Можно написать скрипты для загрузки модов через `curl`/`wget` и складывать их в `mods/server`.
- Придумать cron-задачи для регулярного `make backup` (как только реализуем).

---

Готово! При необходимости можно дополнить документ инструкциями для провайдера, где будет разворачиваться сервер (Hetzner, AWS, OVH и т.п.).
