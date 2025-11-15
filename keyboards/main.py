"""
Main keyboard layouts for the bot
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Расписание на сегодня"),
                KeyboardButton(text="📆 Расписание на неделю")
            ],
            [
                KeyboardButton(text="⚙️ Настройки"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """Get settings keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔔 Уведомления"),
                KeyboardButton(text="🔄 Изменить группу")
            ],
            [
                KeyboardButton(text="◀️ Назад в меню")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard with back button"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="◀️ Назад в меню")]
        ],
        resize_keyboard=True
    )
    return keyboard
