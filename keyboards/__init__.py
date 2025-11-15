"""Keyboards package for the bot."""

from .main import get_main_keyboard, get_back_keyboard, get_cancel_keyboard
from .selection import (
    get_course_keyboard,
    get_group_keyboard,
    get_notifications_keyboard,
    get_time_keyboard,
    get_days_keyboard,
    get_schedule_period_keyboard,
    get_confirmation_keyboard
)

__all__ = [
    'get_main_keyboard',
    'get_back_keyboard',
    'get_cancel_keyboard',
    'get_course_keyboard',
    'get_group_keyboard',
    'get_notifications_keyboard',
    'get_time_keyboard',
    'get_days_keyboard',
    'get_schedule_period_keyboard',
    'get_confirmation_keyboard'
]
