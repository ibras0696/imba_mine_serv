from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(server_label: str) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="Запуск", callback_data="menu:up"),
            InlineKeyboardButton(text="Остановка", callback_data="menu:down"),
        ],
        [
            InlineKeyboardButton(text="Перезапуск", callback_data="menu:restart"),
            InlineKeyboardButton(text="Статус", callback_data="menu:status"),
        ],
        [
            InlineKeyboardButton(text="Логи", callback_data="menu:logs"),
            InlineKeyboardButton(text="Моды", callback_data="menu:mods"),
        ],
        [
            InlineKeyboardButton(text="ENV", callback_data="menu:env"),
            InlineKeyboardButton(text="Миры", callback_data="menu:worlds"),
        ],
        [
            InlineKeyboardButton(text=f"Сервер: {server_label}", callback_data="menu:server"),
        ],
        [
            InlineKeyboardButton(text="OP ibrass", callback_data="op:grant:ibrass"),
            InlineKeyboardButton(text="Снять ibrass", callback_data="op:revoke:ibrass"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(action: str, server_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подтвердить",
                    callback_data=f"confirm:{action}:{server_name}:yes",
                ),
                InlineKeyboardButton(text="Отмена", callback_data="confirm:cancel"),
            ]
        ]
    )


def logs_keyboard(default_lines: int = 100) -> InlineKeyboardMarkup:
    options = [50, default_lines, 200]
    rows = [
        [InlineKeyboardButton(text=f"Логи {lines}", callback_data=f"logs:{lines}") for lines in options],
        [InlineKeyboardButton(text="Назад", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def server_select_keyboard(servers: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"server:select:{name}")]
        for name, label in servers
    ]
    rows.append([InlineKeyboardButton(text="Назад", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def worlds_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="Список миров", callback_data="worlds:list"),
            InlineKeyboardButton(text="Переключить", callback_data="worlds:set"),
        ],
        [
            InlineKeyboardButton(text="Новый мир", callback_data="worlds:new"),
            InlineKeyboardButton(text="Загрузить мир", callback_data="worlds:upload"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
