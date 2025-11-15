from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main keyboard with schedule and settings buttons"""
    keyboard = [
        [
            KeyboardButton(text="📅 Сегодня"),
            KeyboardButton(text="📆 Завтра")
        ],
        [
            KeyboardButton(text="Пн"),
            KeyboardButton(text="Вт"),
            KeyboardButton(text="Ср")
        ],
        [
            KeyboardButton(text="Чт"),
            KeyboardButton(text="Пт"),
            KeyboardButton(text="Сб")
        ],
        [
            KeyboardButton(text="⚙️ Настройки"),
            KeyboardButton(text="👤 Профиль")
        ],
        [
            KeyboardButton(text="❓ Помощь")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
