from __future__ import annotations

import html

from bot.config import Config
from bot.services.shell import run


async def build_status_text(config: Config) -> str:
    if config.remote:
        return "BOT_REMOTE=1 пока не поддерживается для /status.\nОтключи BOT_REMOTE или запусти бота на сервере."

    cmd = (
        f'docker compose --env-file "{config.env_file}" '
        f'-f "{config.compose_file}" ps'
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

    output = stdout or "(нет вывода)"
    return f"Состояние контейнеров:\n<pre>{html.escape(output)}</pre>"
