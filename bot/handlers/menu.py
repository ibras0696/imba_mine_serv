from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard


def register(router: Router, config: Config) -> None:
    @router.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        await message.answer(
            "Привет! Бот управляет сервером Imba Mine. Выбирай команду ниже.",
            reply_markup=main_menu_keyboard(),
        )

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        lines = [
            "Доступные команды:",
            "/status, /ps - состояние контейнеров",
            "/up, /down, /restart - управление сервером",
            "/logs [50|100|200] - просмотр логов",
            "/start - открыть главное меню",
        ]
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard())
