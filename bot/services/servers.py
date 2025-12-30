from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from bot.config import Config, ServerProfile


@dataclass
class SelectedServer:
    name: str
    profile: ServerProfile


_selected_by_chat: Dict[int, str] = {}


def list_servers(config: Config) -> Iterable[ServerProfile]:
    return config.servers.values()


def get_selected_server(config: Config, chat_id: int | None) -> SelectedServer:
    name = config.default_server
    if chat_id is not None:
        name = _selected_by_chat.get(chat_id, name)
    if name not in config.servers:
        name = config.default_server
    return SelectedServer(name=name, profile=config.servers[name])


def set_selected_server(chat_id: int, name: str) -> None:
    _selected_by_chat[chat_id] = name


def env_key(server: ServerProfile, key: str) -> str:
    prefix = server.env_prefix or ""
    return f"{prefix}{key}".upper()
