from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services.mods import build_mods_text
from bot.services.servers import get_selected_server


def register(router: Router, config: Config) -> None:
    @router.message(Command("mods"))
    async def cmd_mods(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        await message.answer(build_mods_text(config), reply_markup=main_menu_keyboard(selected.profile.label))

    @router.callback_query(F.data == "menu:mods")
    async def inline_mods(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer(build_mods_text(config), reply_markup=main_menu_keyboard(selected.profile.label))
        await callback.answer()
