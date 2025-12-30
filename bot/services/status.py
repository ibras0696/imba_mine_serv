from __future__ import annotations

from bot.config import Config, ServerProfile
from bot.services.control import make_ps


async def build_status_text(config: Config, server: ServerProfile) -> str:
    result = await make_ps(config, server)
    return result.text
