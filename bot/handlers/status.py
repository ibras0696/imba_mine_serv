from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services.status import build_status_text


def register(router: Router, config: Config) -> None:
    async def _send_status_message(target: Message | CallbackQuery) -> None:
        text = await build_status_text(config)
        if isinstance(target, Message):
            await target.answer(text, reply_markup=main_menu_keyboard())
        else:
            await target.message.edit_text(text, reply_markup=main_menu_keyboard())
            await target.answer()

    @router.message(Command("status"))
    async def cmd_status(message: Message) -> None:
        await _send_status_message(message)

    @router.callback_query(F.data == "menu:status")
    async def inline_status(callback: CallbackQuery) -> None:
        await _send_status_message(callback)
