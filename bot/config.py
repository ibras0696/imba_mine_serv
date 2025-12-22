from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv


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


def _str_to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> Config:
    base_dir = Path(__file__).resolve().parent.parent
    dotenv_path = os.environ.get("BOT_ENV_FILE", base_dir / ".env.bot")
    load_dotenv(dotenv_path)

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN не задан в .env.bot")

    admins_raw = os.environ.get("TELEGRAM_ADMINS", "")
    admin_ids = [int(item.strip()) for item in admins_raw.split(",") if item.strip()]

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
    )
