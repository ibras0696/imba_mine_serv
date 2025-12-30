from __future__ import annotations

import html

from bot.config import Config, ServerProfile
from bot.services.control import CommandResult
from bot.services.shell import run


def _quote(value: str) -> str:
    escaped = value.replace('"', r'\"')
    return f'"{escaped}"'


async def _execute_rcon(
    config: Config,
    server: ServerProfile,
    subcommand: str,
    success_message: str,
) -> CommandResult:
    if config.remote:
        return CommandResult(
            ok=False,
            text=(
                "BOT_REMOTE=1: локальные RCON-команды недоступны.\n"
                f"Команда: <code>{html.escape(subcommand)}</code>"
            ),
        )

    cmd = f"docker exec {server.container} rcon-cli {subcommand}"
    code, stdout, stderr = await run(cmd, workdir=server.workdir, dry_run=config.dry_run)

    if config.dry_run:
        return CommandResult(
            ok=True,
            text=(
                "BOT_DRY_RUN=1: команда не выполнялась.\n"
                f"<code>{html.escape(cmd)}</code>"
            ),
            stdout=stdout,
            stderr=stderr,
        )

    if code != 0:
        error_text = stderr or stdout or "неизвестная ошибка"
        return CommandResult(
            ok=False,
            text=(
                f"RCON-команда завершилась с ошибкой (exit {code}).\n"
                f"<pre>{html.escape(error_text)}</pre>"
            ),
            stdout=stdout,
            stderr=stderr,
        )

    return CommandResult(ok=True, text=success_message, stdout=stdout, stderr=stderr)


async def op_player(config: Config, server: ServerProfile, player: str) -> CommandResult:
    player = player.strip()
    if not player:
        return CommandResult(ok=False, text="Ник пустой")
    quoted = _quote(player)
    return await _execute_rcon(config, server, f"op {quoted}", f"OP выдан игроку {html.escape(player)}")


async def deop_player(config: Config, server: ServerProfile, player: str) -> CommandResult:
    player = player.strip()
    if not player:
        return CommandResult(ok=False, text="Ник пустой")
    quoted = _quote(player)
    return await _execute_rcon(config, server, f"deop {quoted}", f"OP снят у игрока {html.escape(player)}")
