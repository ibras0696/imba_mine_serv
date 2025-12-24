from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services.mods import build_mods_text


def _target_message(target: Message | CallbackQuery) -> Message:
    if isinstance(target, Message):
        return target
    return target.message


async def _reply(target: Message | CallbackQuery, text: str) -> None:
    message = _target_message(target)
    await message.answer(text, reply_markup=main_menu_keyboard())
    if isinstance(target, CallbackQuery):
        await target.answer()


def register(router: Router, config: Config) -> None:
    @router.message(Command("mods"))
    async def cmd_mods(message: Message) -> None:
        await _reply(message, build_mods_text(config))

    @router.callback_query(F.data == "menu:mods")
    async def inline_mods(callback: CallbackQuery) -> None:
        await _reply(callback, build_mods_text(config))
