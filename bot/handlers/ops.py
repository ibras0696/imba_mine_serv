from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services import rcon

QUICK_PLAYER = "ibrass"


def register(router: Router, config: Config) -> None:
    async def _reply(target: Message | CallbackQuery, text: str) -> None:
        if isinstance(target, Message):
            await target.answer(text, reply_markup=main_menu_keyboard())
        else:
            await target.message.answer(text, reply_markup=main_menu_keyboard())
            await target.answer()

    async def _handle_op(target: Message | CallbackQuery, player: str) -> None:
        result = await rcon.op_player(config, player)
        await _reply(target, result.text)

    async def _handle_deop(target: Message | CallbackQuery, player: str) -> None:
        result = await rcon.deop_player(config, player)
        await _reply(target, result.text)

    @router.message(Command("op"))
    async def cmd_op(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /op ник", reply_markup=main_menu_keyboard())
            return
        await _handle_op(message, parts[1].strip())

    @router.message(Command("deop"))
    async def cmd_deop(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /deop ник", reply_markup=main_menu_keyboard())
            return
        await _handle_deop(message, parts[1].strip())

    @router.callback_query(F.data == "op:grant:ibrass")
    async def quick_op(callback: CallbackQuery) -> None:
        await _handle_op(callback, QUICK_PLAYER)

    @router.callback_query(F.data == "op:revoke:ibrass")
    async def quick_deop(callback: CallbackQuery) -> None:
        await _handle_deop(callback, QUICK_PLAYER)
