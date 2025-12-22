from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_BUTTONS = [
    [("Запуск", "menu:up"), ("Остановка", "menu:down")],
    [("Перезапуск", "menu:restart"), ("Статус", "menu:status")],
    [("Логи", "menu:logs"), ("Обновить статус", "menu:status")],
    [("OP ibrass", "op:grant:ibrass"), ("Снять ibrass", "op:revoke:ibrass")],
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
        for row in MAIN_BUTTONS
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm:{action}:yes"),
                InlineKeyboardButton(text="Отмена", callback_data="confirm:cancel"),
            ]
        ]
    )


def logs_keyboard(default_lines: int = 100) -> InlineKeyboardMarkup:
    options = [50, default_lines, 200]
    rows = [
        [InlineKeyboardButton(text=f"Логи {lines}", callback_data=f"logs:{lines}") for lines in options],
        [InlineKeyboardButton(text="Назад", callback_data="menu:status")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
