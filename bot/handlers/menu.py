from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services.servers import get_selected_server


def register(router: Router, config: Config) -> None:
    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        await message.answer(
            "Привет! Я бот управления сервером. Выбирай действия кнопками ниже.",
            reply_markup=main_menu_keyboard(selected.profile.label),
        )

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        lines = [
            "Команды доступны через кнопки:",
            "Запуск — поднять сервер",
            "Остановка — остановить сервер",
            "Перезапуск — перезапустить сервер",
            "Статус — состояние контейнеров",
            "Логи — последние строки логов",
            "Моды — список модов с ссылками",
            "ENV — просмотр/правка .env",
            "Миры — список/переключение/загрузка мира",
            "Сервер — выбор сервера",
        ]
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard(selected.profile.label))
