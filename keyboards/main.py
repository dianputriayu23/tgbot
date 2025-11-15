"""
Main keyboard layouts for the bot.
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Get the main menu keyboard.
    
    Returns:
        Main keyboard layout
    """
    keyboard = [
        [KeyboardButton("📅 Моё расписание"), KeyboardButton("📆 Расписание на дату")],
        [KeyboardButton("👤 Профиль"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("❓ Помощь")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """
    Get keyboard with back button.
    
    Returns:
        Keyboard with back button
    """
    keyboard = [[KeyboardButton("◀️ Назад")]]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Get keyboard with cancel button.
    
    Returns:
        Keyboard with cancel button
    """
    keyboard = [[KeyboardButton("❌ Отмена")]]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
