from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config, ServerProfile
from bot.keyboards import confirm_keyboard, logs_keyboard, main_menu_keyboard
from bot.services import control as control_service
from bot.services.servers import get_selected_server

CONFIRM_ACTIONS = {
    "down": ("Остановить сервер?", control_service.make_down),
    "restart": ("Перезапустить сервер?", control_service.make_restart),
}


def _target_message(target: Message | CallbackQuery) -> Message:
    if isinstance(target, Message):
        return target
    return target.message


def _chat_id(target: Message | CallbackQuery) -> int:
    message = _target_message(target)
    return message.chat.id


async def _reply(target: Message | CallbackQuery, text: str, server: ServerProfile) -> None:
    message = _target_message(target)
    await message.answer(text, reply_markup=main_menu_keyboard(server.label))
    if isinstance(target, CallbackQuery):
        await target.answer()


async def _ask_confirmation(
    target: Message | CallbackQuery,
    action: str,
    server: ServerProfile,
    prompt: str,
) -> None:
    message = _target_message(target)
    await message.answer(prompt, reply_markup=confirm_keyboard(action, server.name))
    if isinstance(target, CallbackQuery):
        await target.answer()


def register(router: Router, config: Config) -> None:
    async def _run_and_reply(target: Message | CallbackQuery, runner) -> None:
        selected = get_selected_server(config, _chat_id(target))
        result = await runner(config, selected.profile)
        await _reply(target, result.text, selected.profile)

    @router.message(Command("up"))
    async def cmd_up(message: Message) -> None:
        await _run_and_reply(message, control_service.make_up)

    @router.callback_query(F.data == "menu:up")
    async def inline_up(callback: CallbackQuery) -> None:
        await _run_and_reply(callback, control_service.make_up)

    @router.message(Command("down"))
    async def cmd_down(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        prompt, _ = CONFIRM_ACTIONS["down"]
        await _ask_confirmation(message, "down", selected.profile, prompt)

    @router.callback_query(F.data == "menu:down")
    async def inline_down(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        prompt, _ = CONFIRM_ACTIONS["down"]
        await _ask_confirmation(callback, "down", selected.profile, prompt)

    @router.message(Command("restart"))
    async def cmd_restart(message: Message) -> None:
        selected = get_selected_server(config, message.chat.id)
        prompt, _ = CONFIRM_ACTIONS["restart"]
        await _ask_confirmation(message, "restart", selected.profile, prompt)

    @router.callback_query(F.data == "menu:restart")
    async def inline_restart(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        prompt, _ = CONFIRM_ACTIONS["restart"]
        await _ask_confirmation(callback, "restart", selected.profile, prompt)

    @router.callback_query(F.data == "confirm:cancel")
    async def confirm_cancel(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer("Отменено.", reply_markup=main_menu_keyboard(selected.profile.label))
        await callback.answer("Отмена")

    @router.callback_query(F.data.startswith("confirm:"))
    async def confirm_action(callback: CallbackQuery) -> None:
        parts = callback.data.split(":")
        if len(parts) != 4:
            await callback.answer("Некорректная команда", show_alert=True)
            return
        _, action, server_name, decision = parts
        if decision != "yes":
            await callback.answer("Действие отменено", show_alert=True)
            return
        entry = CONFIRM_ACTIONS.get(action)
        if not entry:
            await callback.answer("Неизвестное действие", show_alert=True)
            return
        server = config.servers.get(server_name)
        if not server:
            await callback.answer("Сервер не найден", show_alert=True)
            return
        _, runner = entry
        result = await runner(config, server)
        await _reply(callback, result.text, server)

    @router.message(Command("ps"))
    async def cmd_ps(message: Message) -> None:
        await _run_and_reply(message, control_service.make_ps)

    @router.message(Command("logs"))
    async def cmd_logs(message: Message) -> None:
        parts = (message.text or "").split()
        lines = 100
        if len(parts) > 1:
            try:
                lines = int(parts[1])
            except ValueError:
                pass
        selected = get_selected_server(config, message.chat.id)
        result = await control_service.docker_logs(config, selected.profile, lines)
        await _reply(message, result.text, selected.profile)

    @router.callback_query(F.data == "menu:logs")
    async def inline_logs_menu(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer(
            "Сколько строк логов показать?",
            reply_markup=logs_keyboard(),
        )
        await callback.answer()

    @router.callback_query(F.data.startswith("logs:"))
    async def inline_logs(callback: CallbackQuery) -> None:
        try:
            lines = int(callback.data.split(":")[1])
        except (ValueError, IndexError):
            await callback.answer("Некорректный формат", show_alert=True)
            return
        selected = get_selected_server(config, callback.message.chat.id)
        result = await control_service.docker_logs(config, selected.profile, lines)
        await _reply(callback, result.text, selected.profile)

    @router.callback_query(F.data == "menu:main")
    async def inline_main(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        await callback.message.answer("Меню:", reply_markup=main_menu_keyboard(selected.profile.label))
        await callback.answer()
