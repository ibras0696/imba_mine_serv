from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode

from bot.config import Config, load_config
from bot.handlers import control, env, menu, ops, status


def _create_router(config: Config) -> Router:
    router = Router(name="protected")
    router.message.filter(F.from_user.id.in_(config.admin_ids))
    router.callback_query.filter(F.from_user.id.in_(config.admin_ids))
    menu.register(router, config)
    status.register(router, config)
    control.register(router, config)
    ops.register(router, config)
    env.register(router, config)
    return router


def main_router(config: Config) -> Router:
    return _create_router(config)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    if not config.admin_ids:
        raise RuntimeError("TELEGRAM_ADMINS пустой — укажи свой ID в .env.bot")

    bot = Bot(
        token=config.bot_token,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher()
    router = _create_router(config)
    dp.include_router(router)

    logging.info("Bot started (dry_run=%s)", config.dry_run)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
