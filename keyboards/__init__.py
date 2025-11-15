"""Keyboards module initialization"""
from .main import get_main_keyboard, get_settings_keyboard, get_back_keyboard
from .selection import (
    get_base_selection_keyboard,
    get_course_selection_keyboard,
    get_group_selection_keyboard,
    get_notifications_keyboard
)

__all__ = [
    'get_main_keyboard',
    'get_settings_keyboard',
    'get_back_keyboard',
    'get_base_selection_keyboard',
    'get_course_selection_keyboard',
    'get_group_selection_keyboard',
    'get_notifications_keyboard'
]
