from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class PendingAction:
    kind: str
    server_name: str


_pending_by_chat: Dict[int, PendingAction] = {}


def set_pending(chat_id: int, action: PendingAction) -> None:
    _pending_by_chat[chat_id] = action


def get_pending(chat_id: int) -> PendingAction | None:
    return _pending_by_chat.get(chat_id)


def pop_pending(chat_id: int) -> PendingAction | None:
    return _pending_by_chat.pop(chat_id, None)


def clear_pending(chat_id: int) -> None:
    _pending_by_chat.pop(chat_id, None)
