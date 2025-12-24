from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path

from bot.config import Config
from bot.services.shell import run


@dataclass
class CommandResult:
    ok: bool
    text: str
    stdout: str = ""
    stderr: str = ""


def _relative_to_workdir(path: Path, workdir: Path) -> str:
    try:
        return str(path.relative_to(workdir))
    except ValueError:
        return str(path)


def _format_output(stdout: str, stderr: str) -> str:
    def trim(text: str, limit: int) -> str:
        if not text or len(text) <= limit:
            return text
        omitted = len(text) - limit
        return f"...(обрезано {omitted} символов)\n{text[-limit:]}"

    stdout = trim(stdout, 3200)
    stderr = trim(stderr, 1200)

    blocks: list[str] = []
    if stdout:
        blocks.append(f"<pre>{html.escape(stdout)}</pre>")
    if stderr:
        blocks.append(f"<pre>STDERR:\n{html.escape(stderr)}</pre>")
    if not blocks:
        return "<pre>(без вывода)</pre>"
    return "\n".join(blocks)


async def _execute(
    config: Config,
    command: str,
    success_prefix: str,
) -> CommandResult:
    if config.remote:
        return CommandResult(
            ok=False,
            text=(
                "BOT_REMOTE=1 пока не поддерживается для этой операции.\n"
                f"<code>{html.escape(command)}</code>"
            ),
        )

    code, stdout, stderr = await run(command, workdir=config.workdir, dry_run=config.dry_run)

    if config.dry_run:
        return CommandResult(
            ok=True,
            text=f"BOT_DRY_RUN=1 - команда не запускалась.\n<code>{html.escape(command)}</code>",
            stdout=stdout,
            stderr=stderr,
        )

    if code != 0:
        error_block = stderr or stdout or "неизвестная ошибка"
        return CommandResult(
            ok=False,
            text=(
                f"Ошибка при выполнении команды (exit {code}).\n"
                f"<pre>{html.escape(error_block)}</pre>"
            ),
            stdout=stdout,
            stderr=stderr,
        )

    return CommandResult(
        ok=True,
        text=f"{success_prefix}\n{_format_output(stdout, stderr)}",
        stdout=stdout,
        stderr=stderr,
    )


def _compose_prefix(config: Config) -> str:
    env_rel = _relative_to_workdir(config.env_file, config.workdir)
    compose_rel = _relative_to_workdir(config.compose_file, config.workdir)
    return f'docker compose --env-file "{env_rel}" -f "{compose_rel}"'


def _format_publishers(publishers: list[dict] | None) -> str:
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


def _parse_compose_ps(stdout: str) -> list[dict]:
    if not stdout:
        return []
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []
    except json.JSONDecodeError:
        items: list[dict] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                items.append(item)
        return items


def _format_compose_ps(stdout: str) -> str:
    data = _parse_compose_ps(stdout)
    if not data:
        return "<pre>(контейнеры не найдены)</pre>"
    lines: list[str] = []
    for item in data:
        service = item.get("Service") or item.get("Name") or "unknown"
        state = item.get("State") or "unknown"
        status = item.get("Status") or ""
        ports = _format_publishers(item.get("Publishers"))
        line = f"{service}: {state}"
        if status:
            line += f" — {status}"
        if ports:
            line += f" — порты: {ports}"
        lines.append(line)
    if not lines:
        return "<pre>(контейнеры не найдены)</pre>"
    return f"<pre>{html.escape('\\n'.join(lines))}</pre>"


async def make_up(config: Config) -> CommandResult:
    cmd = f'{_compose_prefix(config)} up -d minecraft'
    return await _execute(config, cmd, "Сервер запускается:")


async def make_down(config: Config) -> CommandResult:
    cmd = f'{_compose_prefix(config)} stop minecraft'
    return await _execute(config, cmd, "Сервер останавливается:")


async def make_restart(config: Config) -> CommandResult:
    cmd = f'{_compose_prefix(config)} restart minecraft'
    return await _execute(config, cmd, "Команда перезапуска отправлена:")


async def make_ps(config: Config) -> CommandResult:
    if config.remote:
        return CommandResult(
            ok=False,
            text="BOT_REMOTE=1 пока не поддерживается для этой операции.",
        )
    cmd = f'{_compose_prefix(config)} ps --format json'
    code, stdout, stderr = await run(cmd, workdir=config.workdir, dry_run=config.dry_run)
    if config.dry_run:
        return CommandResult(
            ok=True,
            text=f"BOT_DRY_RUN=1 - команда не запускалась.\n<code>{html.escape(cmd)}</code>",
            stdout=stdout,
            stderr=stderr,
        )
    if code != 0:
        fallback_cmd = f'{_compose_prefix(config)} ps'
        return await _execute(config, fallback_cmd, "Текущее состояние контейнеров:")
    formatted = _format_compose_ps(stdout)
    return CommandResult(
        ok=True,
        text=f"Текущее состояние контейнеров:\n{formatted}",
        stdout=stdout,
        stderr=stderr,
    )


async def docker_logs(config: Config, lines: int) -> CommandResult:
    if lines <= 0:
        lines = 100
    cmd = (
        f'{_compose_prefix(config)} logs --no-color --tail {lines} minecraft'
    )
    return await _execute(config, cmd, f"Последние {lines} строк логов сервера:")
