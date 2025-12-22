from __future__ import annotations

import html

from bot.config import Config
from bot.services.control import CommandResult
from bot.services.shell import run


def _quote(value: str) -> str:
    escaped = value.replace('"', r'\"')
    return f'"{escaped}"'


async def _execute_rcon(config: Config, subcommand: str, success_message: str) -> CommandResult:
    if config.remote:
        return CommandResult(
            ok=False,
            text=(
                "BOT_REMOTE=1 пока не поддерживается для RCON-команд.\n"
                f"Команда: <code>{html.escape(subcommand)}</code>"
            ),
        )

    cmd = f"docker exec forge-server rcon-cli {subcommand}"
    code, stdout, stderr = await run(cmd, workdir=config.workdir, dry_run=config.dry_run)

    if config.dry_run:
        return CommandResult(
            ok=True,
            text=f"BOT_DRY_RUN=1 — RCON-команда не выполнялась.\n<code>{html.escape(cmd)}</code>",
            stdout=stdout,
            stderr=stderr,
        )

    if code != 0:
        error_text = stderr or stdout or "неизвестная ошибка"
        return CommandResult(
            ok=False,
            text=f"RCON-команда завершилась с ошибкой (exit {code}).\n<pre>{html.escape(error_text)}</pre>",
            stdout=stdout,
            stderr=stderr,
        )

    return CommandResult(ok=True, text=success_message, stdout=stdout, stderr=stderr)


async def op_player(config: Config, player: str) -> CommandResult:
    player = player.strip()
    if not player:
        return CommandResult(ok=False, text="Ник не указан")
    quoted = _quote(player)
    return await _execute_rcon(config, f"op {quoted}", f"OP выдан игроку {html.escape(player)}")


async def deop_player(config: Config, player: str) -> CommandResult:
    player = player.strip()
    if not player:
        return CommandResult(ok=False, text="Ник не указан")
    quoted = _quote(player)
    return await _execute_rcon(config, f"deop {quoted}", f"OP снят с игрока {html.escape(player)}")
