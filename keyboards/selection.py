"""
Selection keyboard layouts for choosing base, course, and group
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_base_selection_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for base selection (9 or 11 classes)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="9 классов", callback_data="base_9"),
                InlineKeyboardButton(text="11 классов", callback_data="base_11")
            ]
        ]
    )
    return keyboard


def get_course_selection_keyboard(base: int) -> InlineKeyboardMarkup:
    """Get keyboard for course selection based on base"""
    if base == 9:
        # Base 9 has courses 1-3
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1 курс", callback_data="course_1"),
                    InlineKeyboardButton(text="2 курс", callback_data="course_2"),
                    InlineKeyboardButton(text="3 курс", callback_data="course_3")
                ],
                [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_base")]
            ]
        )
    else:
        # Base 11 has courses 1-2
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1 курс", callback_data="course_1"),
                    InlineKeyboardButton(text="2 курс", callback_data="course_2")
                ],
                [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_base")]
            ]
        )
    return keyboard


def get_group_selection_keyboard(groups: List[str], base: int, course: int) -> InlineKeyboardMarkup:
    """Get keyboard for group selection"""
    buttons = []
    
    # Create buttons in rows of 2
    for i in range(0, len(groups), 2):
        row = []
        row.append(InlineKeyboardButton(
            text=groups[i], 
            callback_data=f"group_{groups[i]}"
        ))
        if i + 1 < len(groups):
            row.append(InlineKeyboardButton(
                text=groups[i + 1], 
                callback_data=f"group_{groups[i + 1]}"
            ))
        buttons.append(row)
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_course")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_notifications_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    """Get keyboard for notification settings"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Включить" if not enabled else "✅ Включено",
                    callback_data="notif_on"
                ),
                InlineKeyboardButton(
                    text="❌ Выключить" if enabled else "❌ Выключено",
                    callback_data="notif_off"
                )
            ]
        ]
    )
    return keyboard
