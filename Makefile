# ===========================================
# Makefile для управления сервером Minecraft
# ===========================================
SHELL := bash

COMPOSE_FILE := docker-compose.yml
ENV_FILE ?= env/local.env
DOCKER_COMPOSE := docker compose
PYTHON ?= py
AUTO_FETCH_MODS ?= 0
PLINK ?= tools/plink.exe
SSH_HOST ?= root@0.0.0.0
SSH_PASSWORD ?=

MAIN_SERVICE := minecraft
SHOOTER_SERVICE := minecraft_shooter
VANILLA_SERVICE := minecraft_vanilla
BOT_SERVICE := bot

MAIN_CONTAINER := forge-server
SHOOTER_CONTAINER := forge-server-shooter
VANILLA_CONTAINER := forge-server-vanilla

SERVER ?= main
ifeq ($(SERVER),shooter)
SERVICE := $(SHOOTER_SERVICE)
CONTAINER := $(SHOOTER_CONTAINER)
else ifeq ($(SERVER),vanilla)
SERVICE := $(VANILLA_SERVICE)
CONTAINER := $(VANILLA_CONTAINER)
else
SERVICE := $(MAIN_SERVICE)
CONTAINER := $(MAIN_CONTAINER)
endif

.PHONY: help up up-all up-one up-shooter down stop stop-all restart restart-all logs ps clean clean-local clean-data rebuild fetch-mods fetch-mods-server forge-installer op op-ibrass remote-op remote-op-ibrass kick kick-ibrass players remote-players

help:
	@echo "Доступные команды:"
	@echo "  make up                - поднять основной сервер + бот"
	@echo "  make up-all            - поднять все сервера + бот"
	@echo "  make up-one SERVER=... - поднять только один сервер (main|shooter|vanilla)"
	@echo "  make up-shooter        - поднять shooter-сервер"
	@echo "  make up-bot            - поднять только Telegram-бота"
	@echo "  make down              - остановить и удалить все контейнеры"
	@echo "  make stop SERVER=...   - остановить один сервер (main|shooter|vanilla)"
	@echo "  make stop-bot          - остановить только Telegram-бота"
	@echo "  make stop-all          - остановить все сервисы"
	@echo "  make restart           - перезапустить выбранный сервер (SERVER=main|shooter|vanilla)"
	@echo "  make restart-all       - перезапустить оба сервера + бот"
	@echo "  make logs SERVER=...   - показать логи сервера (main|shooter|vanilla)"
	@echo "  make ps                - статус контейнеров"
	@echo "  make clean             - docker compose down -v (без удаления данных)"
	@echo "  make clean-data        - удалить data/main, data/shooter, data/vanilla и backups (ОПАСНО)"
	@echo "  make clean-local       - удалить локальные Python-кэши"
	@echo "  make rebuild           - пересобрать образы без кеша"
	@echo "  make forge-installer   - скачать Forge installer в docker/artifacts"
	@echo "  make fetch-mods        - скачать моды (server+client)"
	@echo "  make fetch-mods-server - скачать моды только для сервера"
	@echo "  make op PLAYER=Nick    - выдать OP на выбранном сервере"
	@echo "  make kick PLAYER=Nick  - кикнуть игрока на выбранном сервере"
	@echo "  make players           - список игроков на выбранном сервере"

up:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@if [ "$(AUTO_FETCH_MODS)" = "1" ]; then \
		$(MAKE) fetch-mods-server; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d $(MAIN_SERVICE) $(BOT_SERVICE)
	@if docker ps --format '{{.Names}}' | grep -q '^$(MAIN_CONTAINER)$$'; then \
		bash git/scripts/grant_ops.sh "$(ENV_FILE)" "make-up"; \
	else \
		echo "$(MAIN_CONTAINER) не найден, пропускаю grant_ops"; \
	fi

up-all:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@if [ "$(AUTO_FETCH_MODS)" = "1" ]; then \
		$(MAKE) fetch-mods-server; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d $(MAIN_SERVICE) $(SHOOTER_SERVICE) $(VANILLA_SERVICE) $(BOT_SERVICE)

up-one:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d $(SERVICE)

up-shooter:
	$(MAKE) up-one SERVER=shooter

up-bot:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d $(BOT_SERVICE)

down:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down

stop:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop $(SERVICE)

stop-bot:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop $(BOT_SERVICE)

stop-all:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) stop

restart:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart $(SERVICE)

restart-all:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) restart

logs:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) logs -f $(SERVICE)

ps:
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) ps

clean:
	@echo "Остановит контейнеры и удалит анонимные volumes. Данные на bind-mount не трогаются."
	@read -p "Продолжить? (yes/NO) " ans && [ "$$ans" = "yes" ]
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) down -v

clean-data:
	@echo "Удалит data/main, data/shooter, data/vanilla и backups. Это необратимо."
	@read -p "Точно удалить? (yes/NO) " ans && [ "$$ans" = "yes" ]
	@rm -rf ./data/main ./data/shooter ./data/vanilla ./backups

clean-local:
	@echo "Чищу локальные Python-кэши..."
	@find . -path "./.venv" -prune -o -path "./data" -prune -o -path "./logs" -prune -o -name "__pycache__" -type d -exec rm -rf {} +
	@find . -path "./.venv" -prune -o -name "*.pyc" -o -name "*.pyo" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name ".coverage" -o -name ".coverage.*" -exec rm -rf {} +

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

fetch-mods-server:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@set -a; . $(ENV_FILE); set +a; \
		$(PYTHON) git/scripts/fetch_modrinth.py server; \
		if [ -n "$$CURSEFORGE_API_KEY" ]; then \
			$(PYTHON) git/scripts/fetch_curseforge.py; \
		else \
			echo "INFO: CURSEFORGE_API_KEY не задан, пропускаю CurseForge."; \
		fi; \
		bash git/scripts/download_mods.sh server

forge-installer:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	@set -a; . $(ENV_FILE); set +a; \
		bash git/scripts/download_forge.sh "$$MC_VERSION" "$$FORGE_VERSION"

op:
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make op PLAYER=Nick [SERVER=main|shooter]"; \
		exit 1; \
	fi
	docker exec $(CONTAINER) rcon-cli op $(PLAYER)

op-ibrass:
	$(MAKE) op PLAYER=ibrass

remote-op:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Используй: make remote-op SSH_PASSWORD=... PLAYER=Nick)
endif
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make remote-op SSH_PASSWORD=... PLAYER=Nick"; \
		exit 1; \
	fi
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec $(CONTAINER) rcon-cli op $(PLAYER)"

kick:
	@if [ -z "$(PLAYER)" ]; then \
		echo "Использование: make kick PLAYER=Nick [SERVER=main|shooter]"; \
		exit 1; \
	fi
	docker exec $(CONTAINER) rcon-cli kick $(PLAYER)

kick-ibrass:
	$(MAKE) kick PLAYER=ibrass

players:
	docker exec $(CONTAINER) rcon-cli list

remote-players:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Используй: make remote-players SSH_PASSWORD=...)
endif
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec $(CONTAINER) rcon-cli list"

remote-op-ibrass:
ifeq ($(strip $(SSH_PASSWORD)),)
	$(error SSH_PASSWORD не задан. Используй: make remote-op-ibrass SSH_PASSWORD=...)
endif
	$(PLINK) -ssh $(SSH_HOST) -pw "$(SSH_PASSWORD)" "docker exec $(CONTAINER) rcon-cli op ibrass"
