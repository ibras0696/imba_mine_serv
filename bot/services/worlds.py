from __future__ import annotations

import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from bot.config import ServerProfile
from bot.services import env_file
from bot.services.servers import env_key

MAX_BACKUPS = 3


@dataclass
class WorldEntry:
    name: str
    path: Path


def get_current_world(server: ServerProfile) -> str | None:
    return env_file.get_value(server.env_file, env_key(server, "LEVEL_NAME"))


def list_worlds(server: ServerProfile) -> list[WorldEntry]:
    data_dir = server.data_dir
    if not data_dir.exists():
        return []
    worlds: list[WorldEntry] = []
    for item in data_dir.iterdir():
        if not item.is_dir():
            continue
        if (item / "level.dat").exists():
            worlds.append(WorldEntry(name=item.name, path=item))
    return sorted(worlds, key=lambda w: w.name.lower())


def ensure_world_name(raw: str) -> str:
    name = raw.strip()
    if not name:
        raise ValueError("Имя мира пустое")
    if "/" in name or "\\" in name:
        raise ValueError("Недопустимые символы в имени мира")
    return name


def ensure_data_dir(server: ServerProfile) -> None:
    server.data_dir.mkdir(parents=True, exist_ok=True)


def backup_world(server: ServerProfile, world_name: str) -> Path:
    ensure_data_dir(server)
    src = server.data_dir / world_name
    if not src.exists():
        raise FileNotFoundError(f"Мир {world_name} не найден")
    server.backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    archive_base = server.backup_dir / f"{world_name}-{timestamp}"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=server.data_dir, base_dir=world_name)
    _trim_backups(server.backup_dir, MAX_BACKUPS)
    return Path(archive_path)


def _trim_backups(backup_dir: Path, max_items: int) -> None:
    if max_items <= 0:
        return
    archives = sorted(backup_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in archives[max_items:]:
        try:
            old.unlink()
        except OSError:
            continue


def download_to_path(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request) as response, destination.open("wb") as target:
        shutil.copyfileobj(response, target)


def _zip_has_level(zip_file: zipfile.ZipFile) -> list[str]:
    return [name for name in zip_file.namelist() if name.endswith("level.dat")]


def _safe_extract(zip_file: zipfile.ZipFile, prefix: str, target_dir: Path) -> None:
    target_root = target_dir.resolve()
    for member in zip_file.infolist():
        filename = member.filename
        if not filename or filename.endswith("/"):
            continue
        if not filename.startswith(prefix):
            continue
        relative = filename[len(prefix):]
        if not relative:
            continue
        dest = (target_dir / relative).resolve()
        if not dest.is_relative_to(target_root):
            raise ValueError("Архив содержит небезопасные пути")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(member) as source, dest.open("wb") as output:
            shutil.copyfileobj(source, output)


def extract_world_zip(zip_path: Path, target_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as archive:
        level_entries = _zip_has_level(archive)
        if not level_entries:
            raise ValueError("В архиве нет level.dat")
        prefix = ""
        if all("/" in entry for entry in level_entries):
            prefix = level_entries[0].rsplit("/", 1)[0] + "/"
        _safe_extract(archive, prefix, target_dir)


def set_level_name(server: ServerProfile, world_name: str) -> Path:
    return env_file.set_value(server.env_file, env_key(server, "LEVEL_NAME"), world_name).backup_path


def clear_seed(server: ServerProfile) -> None:
    env_file.set_value(server.env_file, env_key(server, "SEED"), "")


def remove_world_dir(server: ServerProfile, world_name: str) -> None:
    target = server.data_dir / world_name
    if target.exists():
        shutil.rmtree(target)


def prepare_world_dir(server: ServerProfile, world_name: str) -> Path:
    ensure_data_dir(server)
    target = server.data_dir / world_name
    if target.exists():
        raise FileExistsError(f"Мир {world_name} уже существует")
    target.mkdir(parents=True, exist_ok=False)
    return target


def world_names(entries: Iterable[WorldEntry]) -> list[str]:
    return [entry.name for entry in entries]
