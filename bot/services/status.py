from __future__ import annotations

import html
import json

from bot.config import Config
from bot.services.shell import run


async def build_status_text(config: Config) -> str:
    if config.remote:
        return "BOT_REMOTE=1 пока не поддерживается для /status.\nОтключи BOT_REMOTE или запусти бота на сервере."

    cmd = (
        f'docker compose --env-file "{config.env_file}" '
        f'-f "{config.compose_file}" ps --format json'
    )
    code, stdout, stderr = await run(cmd, workdir=config.workdir, dry_run=config.dry_run)

    if config.dry_run:
        escaped = html.escape(cmd)
        return f"BOT_DRY_RUN=1 — команда не выполнялась.\n<code>{escaped}</code>"

    if code != 0:
        error_text = stderr or stdout or "неизвестная ошибка"
        return (
            f"docker compose ps завершился с ошибкой (code {code}).\n"
            f"<pre>{html.escape(error_text)}</pre>"
        )

    if not stdout:
        return "Состояние контейнеров:\n<pre>(контейнеры не найдены)</pre>"

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        output = stdout or "(нет вывода)"
        return f"Состояние контейнеров:\n<pre>{html.escape(output)}</pre>"

    if not data:
        return "Состояние контейнеров:\n<pre>(контейнеры не найдены)</pre>"

    def format_ports(publishers: list[dict] | None) -> str:
        if not publishers:
            return ""
        parts: list[str] = []
        for publisher in publishers:
            if not isinstance(publisher, dict):
                continue
            target = publisher.get("TargetPort")
            published = publisher.get("PublishedPort")
            proto = publisher.get("Protocol")
            host = publisher.get("URL") or "0.0.0.0"
            if published and target:
                parts.append(f"{host}:{published}->{target}/{proto}")
            elif target:
                parts.append(f"{target}/{proto}")
        return ", ".join(parts)

    lines: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        service = item.get("Service") or item.get("Name") or "unknown"
        state = item.get("State") or "unknown"
        status = item.get("Status") or ""
        ports = format_ports(item.get("Publishers"))
        line = f"{service}: {state}"
        if status:
            line += f" — {status}"
        if ports:
            line += f" — порты: {ports}"
        lines.append(line)

    output = "\n".join(lines) if lines else "(контейнеры не найдены)"
    return f"Состояние контейнеров:\n<pre>{html.escape(output)}</pre>"
