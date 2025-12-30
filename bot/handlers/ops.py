from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services import rcon
from bot.services.servers import get_selected_server

QUICK_PLAYER = "ibrass"


def register(router: Router, config: Config) -> None:
    async def _reply(target: Message | CallbackQuery, text: str) -> None:
        if isinstance(target, Message):
            selected = get_selected_server(config, target.chat.id)
            await target.answer(text, reply_markup=main_menu_keyboard(selected.profile.label))
        else:
            selected = get_selected_server(config, target.message.chat.id)
            await target.message.answer(text, reply_markup=main_menu_keyboard(selected.profile.label))
            await target.answer()

    async def _handle_op(target: Message | CallbackQuery, player: str) -> None:
        selected = get_selected_server(config, _chat_id(target))
        result = await rcon.op_player(config, selected.profile, player)
        await _reply(target, result.text)

    async def _handle_deop(target: Message | CallbackQuery, player: str) -> None:
        selected = get_selected_server(config, _chat_id(target))
        result = await rcon.deop_player(config, selected.profile, player)
        await _reply(target, result.text)

    def _chat_id(target: Message | CallbackQuery) -> int:
        if isinstance(target, Message):
            return target.chat.id
        return target.message.chat.id

    @router.message(Command("op"))
    async def cmd_op(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            selected = get_selected_server(config, message.chat.id)
            await message.answer("Использование: /op Nick", reply_markup=main_menu_keyboard(selected.profile.label))
            return
        await _handle_op(message, parts[1].strip())

    @router.message(Command("deop"))
    async def cmd_deop(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            selected = get_selected_server(config, message.chat.id)
            await message.answer("Использование: /deop Nick", reply_markup=main_menu_keyboard(selected.profile.label))
            return
        await _handle_deop(message, parts[1].strip())

    @router.callback_query(F.data == "op:grant:ibrass")
    async def quick_op(callback: CallbackQuery) -> None:
        await _handle_op(callback, QUICK_PLAYER)

    @router.callback_query(F.data == "op:revoke:ibrass")
    async def quick_deop(callback: CallbackQuery) -> None:
        await _handle_deop(callback, QUICK_PLAYER)
