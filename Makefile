# ===========================================
# Makefile — дружелюбная обёртка для Docker
# ===========================================
# Как пользоваться:
# 1. Скопируй env/.env.example → env/local.env и заполни.
# 2. Запусти `make up`, чтобы поднять сервер.
# 3. Остальные команды помогают управлять контейнером.

# Жёстко используем bash, чтобы make в PowerShell не спотыкался
SHELL := bash

# Пути и команды (менять не нужно, если не знаешь зачем)
COMPOSE_FILE := docker-compose.yml
ENV_FILE ?= env/local.env
DOCKER_COMPOSE := docker compose
PYTHON ?= py
PLINK ?= tools/plink.exe
SSH_HOST ?= root@83.147.246.160
SSH_PASSWORD ?=

.PHONY: help up down restart logs ps clean rebuild fetch-mods forge-installer op op-ibrass remote-op remote-op-ibrass kick kick-ibrass players remote-players

help:
	@echo "Доступные команды:"
	@echo "  make up         - поднять сервер (docker compose up -d)"
	@echo "  make down       - остановить сервер"
	@echo "  make restart    - перезапустить (down + up)"
	@echo "  make logs       - посмотреть логи в реальном времени"
	@echo "  make ps         - статус контейнера"
	@echo "  make clean      - удалить контейнер и связанные тома (осторожно)"
	@echo "  make rebuild    - пересобрать образ (после правок Dockerfile)"
	@echo "  make forge-installer - скачать Forge installer в docker/artifacts"
	@echo "  make op PLAYER=Ник - выдать опку через rcon-cli"
	@echo "  make kick PLAYER=Ник - кикнуть игрока через rcon-cli"
	@echo "  make players    - список игроков через rcon-cli list"
	@echo "  make remote-op PLAYER=Ник SSH_PASSWORD=... - выдать опку по SSH (plink)"

up:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d
	@if docker ps --format '{{.Names}}' | grep -q '^forge-server$$'; then \
		bash git/scripts/grant_ops.sh "$(ENV_FILE)" "make-up"; \
	else \
		echo "forge-server не запущен, пропускаю grant_ops"; \
	fi

down:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

restart: down up

logs:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f

ps:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

clean:
	@echo "⚠️  Эта команда удалит контейнеры и тома (мир/конфиги)."
	@read -p "Точно продолжить? (yes/NO) " ans && [ "$$ans" = "yes" ]
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down -v

rebuild:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) build --no-cache

fetch-mods:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@set -a; . $(ENV_FILE); set +a; \
		$(PYTHON) git/scripts/fetch_modrinth.py all; \
		if [ -n "$$CURSEFORGE_API_KEY" ]; then \
			$(PYTHON) git/scripts/fetch_curseforge.py; \
		else \
			echo "INFO: CURSEFORGE_API_KEY не задан, пропускаю CurseForge."; \
		fi

forge-installer:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@set -a; . $(ENV_FILE); set +a; \
		bash git/scripts/download_forge.sh "$${MC_VERSION:-1.20.1}" "$${FORGE_VERSION:-47.4.10}"

op:
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make op PLAYER=Ник"; \
		exit 1; \
	fi
	docker exec forge-server rcon-cli op $(PLAYER)

op-ibrass:
	$(MAKE) op PLAYER=ibrass

remote-op:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Запусти: make remote-op SSH_PASSWORD=... PLAYER=Ник)
endif
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make remote-op PLAYER=Ник SSH_PASSWORD=..."; \
		exit 1; \
	fi
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec forge-server rcon-cli op $(PLAYER)"

# Пример: make kick PLAYER=Notch
kick:
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make kick PLAYER=Ник"; \
		exit 1; \
	fi
	docker exec forge-server rcon-cli kick $(PLAYER)

# Быстрый вызов: make kick-ibrass
kick-ibrass:
	$(MAKE) kick PLAYER=ibrass

# Пример: make players
players:
	docker exec forge-server rcon-cli list

remote-players:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Запусти: make remote-players SSH_PASSWORD=...)
endif
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec forge-server rcon-cli list"


remote-op-ibrass:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Запусти: make remote-op-ibrass SSH_PASSWORD=...)
endif
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec forge-server rcon-cli op ibrass"
