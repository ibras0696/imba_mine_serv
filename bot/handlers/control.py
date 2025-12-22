from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import confirm_keyboard, logs_keyboard, main_menu_keyboard
from bot.services import control as control_service

CONFIRM_ACTIONS = {
    "down": ("Остановить сервер?", control_service.make_down),
    "restart": ("Перезапустить сервер?", control_service.make_restart),
}


def _target_message(target: Message | CallbackQuery) -> Message:
    if isinstance(target, Message):
        return target
    return target.message


async def _reply(
    target: Message | CallbackQuery,
    text: str,
) -> None:
    message = _target_message(target)
    await message.answer(text, reply_markup=main_menu_keyboard())
    if isinstance(target, CallbackQuery):
        await target.answer()


async def _ask_confirmation(target: Message | CallbackQuery, action: str, prompt: str) -> None:
    message = _target_message(target)
    await message.answer(prompt, reply_markup=confirm_keyboard(action))
    if isinstance(target, CallbackQuery):
        await target.answer()


def register(router: Router, config: Config) -> None:
    async def _run_and_reply(
        target: Message | CallbackQuery,
        runner,
    ) -> None:
        result = await runner(config)
        await _reply(target, result.text)

    @router.message(Command("up"))
    async def cmd_up(message: Message) -> None:
        await _run_and_reply(message, control_service.make_up)

    @router.callback_query(F.data == "menu:up")
    async def inline_up(callback: CallbackQuery) -> None:
        await _run_and_reply(callback, control_service.make_up)

    @router.message(Command("down"))
    async def cmd_down(message: Message) -> None:
        prompt, _ = CONFIRM_ACTIONS["down"]
        await _ask_confirmation(message, "down", prompt)

    @router.callback_query(F.data == "menu:down")
    async def inline_down(callback: CallbackQuery) -> None:
        prompt, _ = CONFIRM_ACTIONS["down"]
        await _ask_confirmation(callback, "down", prompt)

    @router.message(Command("restart"))
    async def cmd_restart(message: Message) -> None:
        prompt, _ = CONFIRM_ACTIONS["restart"]
        await _ask_confirmation(message, "restart", prompt)

    @router.callback_query(F.data == "menu:restart")
    async def inline_restart(callback: CallbackQuery) -> None:
        prompt, _ = CONFIRM_ACTIONS["restart"]
        await _ask_confirmation(callback, "restart", prompt)

    @router.callback_query(F.data == "confirm:cancel")
    async def confirm_cancel(callback: CallbackQuery) -> None:
        await callback.message.answer("Операция отменена.", reply_markup=main_menu_keyboard())
        await callback.answer("Отменено")

    @router.callback_query(F.data.startswith("confirm:"))
    async def confirm_action(callback: CallbackQuery) -> None:
        try:
            _, action, decision = callback.data.split(":")
        except ValueError:
            await callback.answer("Некорректные данные", show_alert=True)
            return
        if decision != "yes":
            await callback.answer("Действие отклонено", show_alert=True)
            return
        entry = CONFIRM_ACTIONS.get(action)
        if not entry:
            await callback.answer("Неизвестная операция", show_alert=True)
            return
        _, runner = entry
        await _run_and_reply(callback, runner)

    @router.message(Command("ps"))
    async def cmd_ps(message: Message) -> None:
        await _run_and_reply(message, control_service.make_ps)

    @router.message(Command("logs"))
    async def cmd_logs(message: Message) -> None:
        parts = message.text.split()
        lines = 100
        if len(parts) > 1:
            try:
                lines = int(parts[1])
            except ValueError:
                pass
        await _run_and_reply(message, lambda cfg: control_service.docker_logs(cfg, lines))

    @router.callback_query(F.data == "menu:logs")
    async def inline_logs_menu(callback: CallbackQuery) -> None:
        await callback.message.answer("Сколько строк логов показать?", reply_markup=logs_keyboard())
        await callback.answer()

    @router.callback_query(F.data.startswith("logs:"))
    async def inline_logs(callback: CallbackQuery) -> None:
        try:
            lines = int(callback.data.split(":")[1])
        except (ValueError, IndexError):
            await callback.answer("Неверный формат", show_alert=True)
            return
        await _run_and_reply(callback, lambda cfg: control_service.docker_logs(cfg, lines))
