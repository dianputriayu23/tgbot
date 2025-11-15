"""
Selection keyboards for choosing course, group, etc.
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List


def get_course_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for course selection.
    
    Returns:
        Inline keyboard with course options
    """
    keyboard = [
        [
            InlineKeyboardButton("1 курс", callback_data="course_1"),
            InlineKeyboardButton("2 курс", callback_data="course_2"),
        ],
        [
            InlineKeyboardButton("3 курс", callback_data="course_3"),
            InlineKeyboardButton("4 курс", callback_data="course_4"),
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_group_keyboard(groups: List[str]) -> InlineKeyboardMarkup:
    """
    Get keyboard for group selection.
    
    Args:
        groups: List of available group names
        
    Returns:
        Inline keyboard with group options
    """
    keyboard = []
    
    # Create rows with 2 groups each
    for i in range(0, len(groups), 2):
        row = []
        for j in range(i, min(i + 2, len(groups))):
            row.append(InlineKeyboardButton(
                groups[j], 
                callback_data=f"group_{groups[j]}"
            ))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_course")])
    
    return InlineKeyboardMarkup(keyboard)


def get_notifications_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for notification settings.
    
    Returns:
        Inline keyboard with notification options
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Включить", callback_data="notif_on"),
            InlineKeyboardButton("❌ Выключить", callback_data="notif_off"),
        ],
        [InlineKeyboardButton("⏰ Изменить время", callback_data="notif_time")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_time_keyboard() -> ReplyKeyboardMarkup:
    """
    Get keyboard for time selection.
    
    Returns:
        Reply keyboard with common time options
    """
    keyboard = [
        [KeyboardButton("07:00"), KeyboardButton("08:00"), KeyboardButton("09:00")],
        [KeyboardButton("10:00"), KeyboardButton("11:00"), KeyboardButton("12:00")],
        [KeyboardButton("❌ Отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_days_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for day selection.
    
    Returns:
        Inline keyboard with days of week
    """
    keyboard = [
        [
            InlineKeyboardButton("Понедельник", callback_data="day_понедельник"),
            InlineKeyboardButton("Вторник", callback_data="day_вторник"),
        ],
        [
            InlineKeyboardButton("Среда", callback_data="day_среда"),
            InlineKeyboardButton("Четверг", callback_data="day_четверг"),
        ],
        [
            InlineKeyboardButton("Пятница", callback_data="day_пятница"),
            InlineKeyboardButton("Суббота", callback_data="day_суббота"),
        ],
        [InlineKeyboardButton("Воскресенье", callback_data="day_воскресенье")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_schedule_period_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for schedule period selection.
    
    Returns:
        Inline keyboard with period options
    """
    keyboard = [
        [
            InlineKeyboardButton("📅 Сегодня", callback_data="period_today"),
            InlineKeyboardButton("📆 Завтра", callback_data="period_tomorrow"),
        ],
        [
            InlineKeyboardButton("📅 Эта неделя", callback_data="period_week"),
            InlineKeyboardButton("📆 След. неделя", callback_data="period_next_week"),
        ],
        [InlineKeyboardButton("📅 Выбрать дату", callback_data="period_custom")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for yes/no confirmation.
    
    Returns:
        Inline keyboard with yes/no options
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Нет", callback_data="confirm_no"),
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)
