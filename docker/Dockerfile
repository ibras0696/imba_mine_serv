# Базовый образ берём у itzg/minecraft-server (поддерживает Forge/Mods).
# Так мы получаем готовую установку Java 17 + скрипты запуска сервера.
ARG BASE_IMAGE=itzg/minecraft-server:java17
ARG MC_VERSION=1.20.1

FROM ${BASE_IMAGE}

# Значения по умолчанию можно переопределить через docker-compose и .env
ENV TYPE=FORGE \
    VERSION=${MC_VERSION} \
    INIT_MEMORY=2G \
    MAX_MEMORY=4G

# Если понадобятся дополнительные скрипты/плагины — кладём их в docker/
# и копируем сюда. Пока ничего не добавляем, оставляем образ "чистым".

# Контейнер стартует стандартным entrypoint'ом из базового образа.
