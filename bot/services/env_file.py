from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil


@dataclass
class EnvSetResult:
    key: str
    value: str
    backup_path: Path


def _ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Env-файл {path} не найден")


def _parse_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _write_lines(path: Path, lines: list[str]) -> None:
    content = "\n".join(lines)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def _backup_file(path: Path) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(path.suffix + f".{timestamp}.bak")
    shutil.copy2(path, backup)
    return backup


def _normalize_key(key: str) -> str:
    return key.strip().upper()


def get_value(env_path: Path, key: str) -> str | None:
    _ensure_exists(env_path)
    target = _normalize_key(key)
    for line in _parse_lines(env_path):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        current_key, current_value = stripped.split("=", 1)
        if current_key.strip().upper() == target:
            return current_value.strip()
    return None


def set_value(env_path: Path, key: str, value: str) -> EnvSetResult:
    _ensure_exists(env_path)
    lines = _parse_lines(env_path)
    target = _normalize_key(key)
    new_line = f"{target}={value}"
    updated = False

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        current_key = stripped.split("=", 1)[0].strip().upper()
        if current_key == target:
            lines[idx] = new_line
            updated = True
            break

    if not updated:
        lines.append(new_line)

    backup = _backup_file(env_path)
    _write_lines(env_path, lines)

    return EnvSetResult(key=target, value=value, backup_path=backup)
