from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import Config
from bot.keyboards import main_menu_keyboard, server_select_keyboard
from bot.services.servers import get_selected_server, list_servers, set_selected_server


def register(router: Router, config: Config) -> None:
    @router.callback_query(F.data == "menu:server")
    async def choose_server(callback: CallbackQuery) -> None:
        servers = [(srv.name, srv.label) for srv in list_servers(config)]
        await callback.message.answer(
            "Выбери сервер:",
            reply_markup=server_select_keyboard(servers),
        )
        await callback.answer()

    @router.callback_query(F.data.startswith("server:select:"))
    async def select_server(callback: CallbackQuery) -> None:
        name = callback.data.split(":", 2)[2]
        if name not in config.servers:
            await callback.answer("Сервер не найден", show_alert=True)
            return
        set_selected_server(callback.message.chat.id, name)
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer(
            f"Текущий сервер: {selected.profile.label}",
            reply_markup=main_menu_keyboard(selected.profile.label),
        )
        await callback.answer()
