from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services import env_file

ENV_KEYS = [
    "EULA",
    "SERVER_PORT",
    "MEMORY_MIN",
    "MEMORY_MAX",
    "MAX_PLAYERS",
    "DIFFICULTY",
    "ONLINE_MODE",
    "OPS",
    "VIEW_DISTANCE",
    "LEVEL_NAME",
    "PVP",
    "ALLOW_FLIGHT",
    "ALLOW_NETHER",
    "ENABLE_COMMAND_BLOCK",
]


def _build_env_message(config: Config) -> str:
    lines = ["<b>Конфиг сервера</b>"]
    for key in ENV_KEYS:
        value = env_file.get_value(config, key)
        if value is None:
            rendered = "(нет)"
        else:
            rendered = f"<code>{html.escape(value)}</code>"
        lines.append(f"{key} = {rendered}")
    lines.append("")
    lines.append("Изменить: <code>/env_set KEY VALUE</code>")
    lines.append("Показать: <code>/env_get KEY</code>")
    return "\n".join(lines)


def register(router: Router, config: Config) -> None:
    @router.message(Command("env"))
    async def cmd_env(message: Message) -> None:
        await message.answer(_build_env_message(config), reply_markup=main_menu_keyboard())

    @router.callback_query(F.data == "menu:env")
    async def inline_env(callback: CallbackQuery) -> None:
        await callback.message.answer(_build_env_message(config), reply_markup=main_menu_keyboard())

    @router.message(Command("env_get"))
    async def cmd_env_get(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /env_get KEY", reply_markup=main_menu_keyboard())
            return
        key = parts[1].strip()
        value = env_file.get_value(config, key)
        if value is None:
            await message.answer(
                f"Переменная {key} не найдена в {config.env_file}",
                reply_markup=main_menu_keyboard(),
            )
            return
        await message.answer(
            f"<b>{key.upper()}</b> = <code>{value}</code>",
            reply_markup=main_menu_keyboard(),
        )

    @router.message(Command("env_set"))
    async def cmd_env_set(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("Использование: /env_set KEY VALUE", reply_markup=main_menu_keyboard())
            return
        key = parts[1].strip()
        value = parts[2].strip()
        try:
            result = env_file.set_value(config, key, value)
        except FileNotFoundError:
            await message.answer(
                f"Файл {config.env_file} не найден.",
                reply_markup=main_menu_keyboard(),
            )
            return
        lines = [
            f"Переменная <b>{result.key}</b> обновлена: <code>{result.value}</code>",
            f"Бэкап: <code>{result.backup_path.name}</code>",
            "Перезапусти контейнеры, если настройка влияет на рантайм.",
        ]
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard())
