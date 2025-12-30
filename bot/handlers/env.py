from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard
from bot.services import env_file
from bot.services.servers import env_key, get_selected_server

ENV_KEYS = [
    "EULA",
    "SERVER_PORT",
    "MEMORY_MIN",
    "MEMORY_MAX",
    "MAX_PLAYERS",
    "DIFFICULTY",
    "SERVER_NAME",
    "ONLINE_MODE",
    "OPS",
    "VIEW_DISTANCE",
    "LEVEL_NAME",
    "PVP",
    "ALLOW_FLIGHT",
    "ALLOW_NETHER",
    "ENABLE_COMMAND_BLOCK",
]


def _build_env_message(config: Config, chat_id: int) -> str:
    selected = get_selected_server(config, chat_id)
    server = selected.profile
    lines = [f"<b>ENV для сервера: {html.escape(server.label)}</b>"]
    for key in ENV_KEYS:
        value = env_file.get_value(server.env_file, env_key(server, key))
        if value is None:
            rendered = "(нет)"
        else:
            rendered = f"<code>{html.escape(value)}</code>"
        lines.append(f"{key} = {rendered}")
    lines.append("")
    lines.append("Установить: <code>/env_set KEY VALUE</code>")
    lines.append("Посмотреть: <code>/env_get KEY</code>")
    return "\n".join(lines)


def register(router: Router, config: Config) -> None:
    @router.message(Command("env"))
    async def cmd_env(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        await message.answer(
            _build_env_message(config, message.chat.id),
            reply_markup=main_menu_keyboard(selected.profile.label),
        )

    @router.callback_query(F.data == "menu:env")
    async def inline_env(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer(
            _build_env_message(config, callback.message.chat.id),
            reply_markup=main_menu_keyboard(selected.profile.label),
        )
        await callback.answer()

    @router.message(Command("env_get"))
    async def cmd_env_get(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /env_get KEY", reply_markup=main_menu_keyboard(selected.profile.label))
            return
        key = parts[1].strip()
        env_value = env_file.get_value(selected.profile.env_file, env_key(selected.profile, key))
        if env_value is None:
            await message.answer(
                f"Ключ {key} не найден в {selected.profile.env_file}",
                reply_markup=main_menu_keyboard(selected.profile.label),
            )
            return
        await message.answer(
            f"<b>{key.upper()}</b> = <code>{env_value}</code>",
            reply_markup=main_menu_keyboard(selected.profile.label),
        )

    @router.message(Command("env_set"))
    async def cmd_env_set(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("Использование: /env_set KEY VALUE", reply_markup=main_menu_keyboard(selected.profile.label))
            return
        key = parts[1].strip()
        value = parts[2].strip()
        try:
            result = env_file.set_value(selected.profile.env_file, env_key(selected.profile, key), value)
        except FileNotFoundError:
            await message.answer(
                f"Файл {selected.profile.env_file} не найден.",
                reply_markup=main_menu_keyboard(selected.profile.label),
            )
            return
        lines = [
            f"Ключ <b>{result.key}</b> обновлён: <code>{result.value}</code>",
            f"Бэкап: <code>{result.backup_path.name}</code>",
            "Для применения настроек перезапусти сервер.",
        ]
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard(selected.profile.label))
