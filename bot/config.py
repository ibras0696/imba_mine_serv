from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv


@dataclass
class ServerProfile:
    name: str
    label: str
    service: str
    container: str
    env_prefix: str
    workdir: Path
    compose_file: Path
    env_file: Path
    data_dir: Path
    backup_dir: Path


@dataclass
class Config:
    bot_token: str
    admin_ids: List[int]
    workdir: Path
    compose_file: Path
    env_file: Path
    dry_run: bool
    remote: bool
    plink_path: Path | None
    ssh_host: str | None
    ssh_password: str | None
    servers: Dict[str, ServerProfile]
    default_server: str


def _str_to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path(value: str | None, base: Path, default: Path) -> Path:
    if not value:
        return default
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _parse_admins(raw: str) -> List[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def _server_env_key(name: str) -> str:
    return name.strip().upper().replace("-", "_")


def _load_servers(
    base_workdir: Path,
    base_compose: Path,
    base_env: Path,
) -> tuple[Dict[str, ServerProfile], str]:
    servers_raw = os.environ.get("SERVERS", "main")
    server_names = [item.strip() for item in servers_raw.split(",") if item.strip()]
    if not server_names:
        server_names = ["main"]

    default_server = os.environ.get("DEFAULT_SERVER", server_names[0])

    servers: Dict[str, ServerProfile] = {}
    for name in server_names:
        env_key = _server_env_key(name)
        label = os.environ.get(f"SERVER_{env_key}_LABEL", name)

        if name == "main":
            service_default = "minecraft"
            container_default = "forge-server"
            prefix_default = ""
        else:
            service_default = f"minecraft_{name}"
            container_default = f"forge-server-{name}"
            prefix_default = f"{env_key}_"

        service = os.environ.get(f"SERVER_{env_key}_SERVICE", service_default)
        container = os.environ.get(f"SERVER_{env_key}_CONTAINER", container_default)
        env_prefix = os.environ.get(f"SERVER_{env_key}_ENV_PREFIX", prefix_default)

        workdir = _resolve_path(os.environ.get(f"SERVER_{env_key}_WORKDIR"), base_workdir, base_workdir)
        compose_file = _resolve_path(
            os.environ.get(f"SERVER_{env_key}_COMPOSE_FILE"),
            workdir,
            base_compose,
        )
        env_file = _resolve_path(
            os.environ.get(f"SERVER_{env_key}_ENV_FILE"),
            workdir,
            base_env,
        )
        data_dir_default = workdir / "data" / name
        backup_dir_default = workdir / "backups" / name
        data_dir = _resolve_path(os.environ.get(f"SERVER_{env_key}_DATA_DIR"), workdir, data_dir_default)
        backup_dir = _resolve_path(os.environ.get(f"SERVER_{env_key}_BACKUP_DIR"), workdir, backup_dir_default)

        servers[name] = ServerProfile(
            name=name,
            label=label,
            service=service,
            container=container,
            env_prefix=env_prefix,
            workdir=workdir,
            compose_file=compose_file,
            env_file=env_file,
            data_dir=data_dir,
            backup_dir=backup_dir,
        )

    if default_server not in servers:
        default_server = server_names[0]

    return servers, default_server


def load_config() -> Config:
    base_dir = Path(__file__).resolve().parent.parent
    dotenv_path = os.environ.get("BOT_ENV_FILE", base_dir / ".env.bot")
    load_dotenv(dotenv_path)

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN не задан в .env.bot")

    admins_raw = os.environ.get("TELEGRAM_ADMINS", "")
    admin_ids = _parse_admins(admins_raw)

    workdir = Path(os.environ.get("WORKDIR", base_dir)).resolve()
    compose_file = (workdir / os.environ.get("COMPOSE_FILE", "docker-compose.yml")).resolve()
    env_file = (workdir / os.environ.get("ENV_FILE", "env/production.env")).resolve()

    dry_run = _str_to_bool(os.environ.get("BOT_DRY_RUN"))
    remote = _str_to_bool(os.environ.get("BOT_REMOTE"))

    plink_path = os.environ.get("PLINK_PATH")
    if plink_path:
        plink_path = Path(plink_path).expanduser().resolve()

    ssh_host = os.environ.get("SSH_HOST")
    ssh_password = os.environ.get("SSH_PASSWORD")

    servers, default_server = _load_servers(workdir, compose_file, env_file)

    return Config(
        bot_token=bot_token,
        admin_ids=admin_ids,
        workdir=workdir,
        compose_file=compose_file,
        env_file=env_file,
        dry_run=dry_run,
        remote=remote,
        plink_path=plink_path,
        ssh_host=ssh_host,
        ssh_password=ssh_password,
        servers=servers,
        default_server=default_server,
    )
