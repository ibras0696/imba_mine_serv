from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import Config
from bot.keyboards import main_menu_keyboard, worlds_menu_keyboard
from bot.services import control
from bot.services.servers import get_selected_server
from bot.services.state import PendingAction, clear_pending, get_pending, set_pending
from bot.services import worlds as world_service


async def _list_worlds_text(config: Config, chat_id: int) -> str:
    selected = get_selected_server(config, chat_id)
    current = world_service.get_current_world(selected.profile) or "(не задан)"
    entries = await asyncio.to_thread(world_service.list_worlds, selected.profile)
    names = world_service.world_names(entries)
    lines = [
        f"<b>Сервер:</b> {selected.profile.label}",
        f"<b>Текущий мир:</b> {current}",
    ]
    if names:
        lines.append("<b>Доступные миры:</b>")
        lines.extend([f"- {name}" for name in names])
    else:
        lines.append("Миры не найдены.")
    return "\n".join(lines)


def _world_prompt(action: str) -> str:
    if action == "world_set":
        return "Отправь имя мира для переключения."
    if action == "world_new":
        return "Отправь имя нового мира (будет создан новый мир со случайным сидом)."
    if action == "world_upload":
        return (
            "Отправь ZIP архив мира с подписью (имя мира) или сообщение вида:\n"
            "<code>ИмяМира https://example.com/world.zip</code>"
        )
    return "Отправь параметры."


def register(router: Router, config: Config) -> None:
    def _resolve_server(chat_id: int, server_name: str | None):
        if server_name and server_name in config.servers:
            return config.servers[server_name]
        return get_selected_server(config, chat_id).profile

    async def _stop_server(message: Message, server) -> bool:
        result = await control.make_down(config, server)
        if not result.ok:
            await message.answer(result.text, reply_markup=main_menu_keyboard(server.label))
            return False
        return True

    async def _start_server(message: Message, server) -> bool:
        result = await control.make_up(config, server)
        if not result.ok:
            await message.answer(result.text, reply_markup=main_menu_keyboard(server.label))
            return False
        return True
    @router.callback_query(F.data == "menu:worlds")
    async def menu_worlds(callback: CallbackQuery) -> None:
        text = await _list_worlds_text(config, callback.message.chat.id)
        await callback.message.answer(text, reply_markup=worlds_menu_keyboard())
        await callback.answer()

    @router.message(Command("worlds"))
    async def cmd_worlds(message: Message) -> None:
        text = await _list_worlds_text(config, message.chat.id)
        await message.answer(text, reply_markup=worlds_menu_keyboard())

    @router.callback_query(F.data == "worlds:list")
    async def worlds_list(callback: CallbackQuery) -> None:
        text = await _list_worlds_text(config, callback.message.chat.id)
        await callback.message.answer(text, reply_markup=worlds_menu_keyboard())
        await callback.answer()

    @router.callback_query(F.data == "worlds:set")
    async def worlds_set(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        set_pending(callback.message.chat.id, PendingAction(kind="world_set", server_name=selected.name))
        await callback.message.answer(_world_prompt("world_set"))
        await callback.answer()

    @router.callback_query(F.data == "worlds:new")
    async def worlds_new(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        set_pending(callback.message.chat.id, PendingAction(kind="world_new", server_name=selected.name))
        await callback.message.answer(_world_prompt("world_new"))
        await callback.answer()

    @router.callback_query(F.data == "worlds:upload")
    async def worlds_upload(callback: CallbackQuery) -> None:
        selected = get_selected_server(config, callback.message.chat.id)
        set_pending(callback.message.chat.id, PendingAction(kind="world_upload", server_name=selected.name))
        await callback.message.answer(_world_prompt("world_upload"))
        await callback.answer()

    @router.message(Command("world_set"))
    async def cmd_world_set(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(_world_prompt("world_set"))
            return
        await _handle_world_set(message, parts[1].strip())

    @router.message(Command("world_new"))
    async def cmd_world_new(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(_world_prompt("world_new"))
            return
        await _handle_world_new(message, parts[1].strip())

    @router.message(Command("world_url"))
    async def cmd_world_url(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 3:
            await message.answer(_world_prompt("world_upload"))
            return
        name = parts[1].strip()
        url = parts[2].strip()
        await _handle_world_url(message, name, url)

    @router.message(F.document)
    async def doc_upload(message: Message) -> None:
        pending = get_pending(message.chat.id)
        if not pending or pending.kind != "world_upload":
            return
        await _handle_world_zip(message)

    @router.message()
    async def pending_text(message: Message) -> None:
        pending = get_pending(message.chat.id)
        if not pending:
            return
        if message.text and message.text.startswith("/"):
            return
        if pending.kind == "world_set" and message.text:
            await _handle_world_set(message, message.text, pending.server_name)
            return
        if pending.kind == "world_new" and message.text:
            await _handle_world_new(message, message.text, pending.server_name)
            return
        if pending.kind == "world_upload" and message.text:
            parts = message.text.split()
            if len(parts) >= 2 and parts[1].startswith("http"):
                await _handle_world_url(message, parts[0], parts[1], pending.server_name)
            else:
                await message.answer(_world_prompt("world_upload"))
            return

    async def _handle_world_set(message: Message, world_name: str, server_name: str | None = None) -> None:
        server = _resolve_server(message.chat.id, server_name)
        try:
            target = world_service.ensure_world_name(world_name)
        except ValueError as exc:
            await message.answer(str(exc))
            return

        entries = await asyncio.to_thread(world_service.list_worlds, server)
        available = set(world_service.world_names(entries))
        if target not in available:
            await message.answer("Мир не найден. Сначала добавь его или выбери из списка.")
            return

        clear_pending(message.chat.id)
        current = world_service.get_current_world(server)
        if current == target:
            await message.answer("Этот мир уже активен.", reply_markup=main_menu_keyboard(server.label))
            return

        backup_path = None
        try:
            if not await _stop_server(message, server):
                return
            if current:
                if (server.data_dir / current).exists():
                    backup_path = await asyncio.to_thread(world_service.backup_world, server, current)
            await asyncio.to_thread(world_service.set_level_name, server, target)
            if not await _start_server(message, server):
                return
        except Exception as exc:
            await _start_server(message, server)
            await message.answer(f"Ошибка при переключении мира: {exc}")
            return

        lines = [f"Мир переключен на: <b>{target}</b>"]
        if backup_path:
            lines.append(f"Бэкап: <code>{backup_path.name}</code>")
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard(server.label))

    async def _handle_world_new(message: Message, world_name: str, server_name: str | None = None) -> None:
        server = _resolve_server(message.chat.id, server_name)
        try:
            target = world_service.ensure_world_name(world_name)
        except ValueError as exc:
            await message.answer(str(exc))
            return

        clear_pending(message.chat.id)
        current = world_service.get_current_world(server)

        try:
            if not await _stop_server(message, server):
                return
            if current:
                if (server.data_dir / current).exists():
                    await asyncio.to_thread(world_service.backup_world, server, current)
            await asyncio.to_thread(world_service.prepare_world_dir, server, target)
            await asyncio.to_thread(world_service.set_level_name, server, target)
            await asyncio.to_thread(world_service.clear_seed, server)
            if not await _start_server(message, server):
                return
        except FileExistsError:
            await _start_server(message, server)
            await message.answer("Такой мир уже существует.")
            return
        except Exception as exc:
            await _start_server(message, server)
            await message.answer(f"Ошибка при создании мира: {exc}")
            return

        await message.answer(
            f"Создан новый мир: <b>{target}</b>",
            reply_markup=main_menu_keyboard(server.label),
        )

    async def _handle_world_zip(message: Message) -> None:
        pending = get_pending(message.chat.id)
        if not pending:
            return
        server = _resolve_server(message.chat.id, pending.server_name)

        world_name = (message.caption or "").strip()
        if not world_name:
            await message.answer("Нужна подпись с именем мира.")
            return

        try:
            target_name = world_service.ensure_world_name(world_name)
        except ValueError as exc:
            await message.answer(str(exc))
            return

        clear_pending(message.chat.id)
        temp_dir = Path(tempfile.mkdtemp(prefix="world_zip_"))
        zip_path = temp_dir / "world.zip"
        try:
            file = await message.bot.get_file(message.document.file_id)
            await message.bot.download(file, destination=zip_path)
            await _install_zip_world(message, server, target_name, zip_path)
        finally:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass

    async def _handle_world_url(
        message: Message, world_name: str, url: str, server_name: str | None = None
    ) -> None:
        server = _resolve_server(message.chat.id, server_name)
        try:
            target_name = world_service.ensure_world_name(world_name)
        except ValueError as exc:
            await message.answer(str(exc))
            return

        clear_pending(message.chat.id)
        temp_dir = Path(tempfile.mkdtemp(prefix="world_url_"))
        zip_path = temp_dir / "world.zip"
        try:
            await asyncio.to_thread(world_service.download_to_path, url, zip_path)
            await _install_zip_world(message, server, target_name, zip_path)
        except Exception as exc:
            await message.answer(f"Не удалось скачать или распаковать мир: {exc}")
        finally:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass

    async def _install_zip_world(message: Message, server, target_name: str, zip_path: Path) -> None:
        current = world_service.get_current_world(server)
        backup_path = None
        try:
            if not await _stop_server(message, server):
                return
            if current:
                if (server.data_dir / current).exists():
                    backup_path = await asyncio.to_thread(world_service.backup_world, server, current)
            target_dir = await asyncio.to_thread(world_service.prepare_world_dir, server, target_name)
            try:
                await asyncio.to_thread(world_service.extract_world_zip, zip_path, target_dir)
            except Exception:
                await asyncio.to_thread(world_service.remove_world_dir, server, target_name)
                raise
            await asyncio.to_thread(world_service.set_level_name, server, target_name)
            if not await _start_server(message, server):
                return
        except FileExistsError:
            await _start_server(message, server)
            await message.answer("Мир с таким именем уже существует.")
            return
        except Exception as exc:
            await _start_server(message, server)
            await message.answer(f"Ошибка при установке мира: {exc}")
            return

        lines = [f"Мир установлен: <b>{target_name}</b>"]
        if backup_path:
            lines.append(f"Бэкап: <code>{backup_path.name}</code>")
        await message.answer("\n".join(lines), reply_markup=main_menu_keyboard(server.label))
