from __future__ import annotations

import html
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


def _make_prefix(config: Config) -> str:
    env_rel = _relative_to_workdir(config.env_file, config.workdir)
    compose_rel = _relative_to_workdir(config.compose_file, config.workdir)
    return f'ENV_FILE="{env_rel}" COMPOSE_FILE="{compose_rel}"'


async def make_up(config: Config) -> CommandResult:
    cmd = f'{_make_prefix(config)} make up'
    return await _execute(config, cmd, "Сервер запускается:")


async def make_down(config: Config) -> CommandResult:
    cmd = f'{_make_prefix(config)} make down'
    return await _execute(config, cmd, "Сервер останавливается:")


async def make_restart(config: Config) -> CommandResult:
    cmd = f'{_make_prefix(config)} make restart'
    return await _execute(config, cmd, "Команда перезапуска отправлена:")


async def make_ps(config: Config) -> CommandResult:
    cmd = f'{_make_prefix(config)} make ps'
    return await _execute(config, cmd, "Текущее состояние контейнеров:")


async def docker_logs(config: Config, lines: int) -> CommandResult:
    if lines <= 0:
        lines = 100
    cmd = (
        f'docker compose --env-file "{config.env_file}" '
        f'-f "{config.compose_file}" logs --tail {lines}'
    )
    return await _execute(config, cmd, f"Последние {lines} строк логов:")
