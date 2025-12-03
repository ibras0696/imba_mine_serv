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
COMPOSE_FILE := compose/docker-compose.yml
ENV_FILE ?= env/local.env
DOCKER_COMPOSE := docker compose
PYTHON ?= py

.PHONY: help up down restart logs ps clean rebuild fetch-mods forge-installer

help:
	@echo "Доступные команды:"
	@echo "  make up         - поднять сервер (docker compose up -d)"
	@echo "  make down       - остановить сервер"
	@echo "  make restart    - перезапустить (down + up)"
	@echo "  make logs       - посмотреть логи в реальном времени"
	@echo "  make ps         - статус контейнера"
	@echo "  make clean      - удалить контейнер и связанные тома (осторожно)"
	@echo "  make rebuild    - пересобрать образ (после правок Dockerfile)"
	@echo "  make forge-installer - download Forge installer into docker/artifacts"

up:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "WARNING: файл $(ENV_FILE) не найден. Скопируй env/.env.example -> $(ENV_FILE) и заполни."; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

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
