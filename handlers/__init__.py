"""Handlers package for the bot."""

from .start import get_start_conversation_handler
from .schedule import (
    my_schedule_handler,
    schedule_by_date_handler,
    period_selected,
    date_input_handler
)
from .settings import (
    settings_handler,
    notifications_settings,
    notification_toggle,
    time_input_handler,
    change_group_handler,
    change_course_selected,
    change_group_selected
)
from .profile import profile_handler
from .help import help_handler, about_handler

__all__ = [
    'get_start_conversation_handler',
    'my_schedule_handler',
    'schedule_by_date_handler',
    'period_selected',
    'date_input_handler',
    'settings_handler',
    'notifications_settings',
    'notification_toggle',
    'time_input_handler',
    'change_group_handler',
    'change_course_selected',
    'change_group_selected',
    'profile_handler',
    'help_handler',
    'about_handler'
]
