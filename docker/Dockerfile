# Base image: itzg/minecraft-server with Java 17
ARG BASE_IMAGE=itzg/minecraft-server:java17
ARG MC_VERSION=1.20.1

FROM ${BASE_IMAGE}

# Default Forge settings (can be overridden by docker-compose.yml)
ENV TYPE=FORGE \
    VERSION=${MC_VERSION} \
    INIT_MEMORY=2G \
    MAX_MEMORY=4G
