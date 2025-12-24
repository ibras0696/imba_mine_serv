from __future__ import annotations

import html
import json
from pathlib import Path

from bot.config import Config


def _load_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _format_list(entries: list[dict], exclude_slugs: set[str] | None = None) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        slug = (entry.get("slug") or "").strip()
        name = (entry.get("name") or slug or "unknown").strip()
        if exclude_slugs and slug and slug in exclude_slugs:
            continue
        if slug:
            url = f"https://modrinth.com/mod/{slug}"
            lines.append(f'- <a href="{html.escape(url, quote=True)}">{html.escape(name)}</a>')
        else:
            lines.append(f"- {html.escape(name)}")
    if not lines:
        lines.append("- (пусто)")
    return lines


def build_mods_text(config: Config) -> str:
    base = config.workdir
    server_list = _load_list(base / "mods" / "sources" / "modrinth-server.json")
    client_list = _load_list(base / "mods" / "sources" / "modrinth-client.json")
    server_slugs = {entry.get("slug") for entry in server_list if entry.get("slug")}
    client_only_entries = [entry for entry in client_list if entry.get("slug") not in server_slugs]

    lines: list[str] = ["<b>Моды для игры</b>"]
    lines.append(f"Нужны на сервере и у клиента ({len(server_list)}):")
    lines.extend(_format_list(server_list))
    lines.append("")
    lines.append(f"Только клиент (не ставить на сервер) ({len(client_only_entries)}):")
    lines.extend(_format_list(client_only_entries))
    lines.append("")
    lines.append("Ссылки ведут на Modrinth.")
    return "\n".join(lines)
