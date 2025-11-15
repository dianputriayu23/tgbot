from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_education_base_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting education base (9 or 11 classes)"""
    keyboard = [
        [
            InlineKeyboardButton(text="База 9 классов", callback_data="base_9"),
            InlineKeyboardButton(text="База 11 классов", callback_data="base_11")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_course_keyboard(base: str) -> InlineKeyboardMarkup:
    """Keyboard for selecting course"""
    keyboard = []
    
    if base == "9":
        # Base 9: 3 courses
        keyboard = [
            [InlineKeyboardButton(text="1 курс", callback_data="course_1")],
            [InlineKeyboardButton(text="2 курс", callback_data="course_2")],
            [InlineKeyboardButton(text="3 курс", callback_data="course_3")]
        ]
    else:
        # Base 11: 2 courses
        keyboard = [
            [InlineKeyboardButton(text="1 курс", callback_data="course_1")],
            [InlineKeyboardButton(text="2 курс", callback_data="course_2")]
        ]
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_base")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_group_keyboard(groups: list, base: str, course: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting group"""
    keyboard = []
    
    for group in groups:
        keyboard.append([InlineKeyboardButton(text=group, callback_data=f"group_{group}")])
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_course_{base}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for settings menu"""
    keyboard = [
        [InlineKeyboardButton(text="🔄 Поменять группу", callback_data="change_group")],
        [InlineKeyboardButton(text="🔔 Уведомления о парах", callback_data="toggle_notif_pairs")],
        [InlineKeyboardButton(text="🔔 Уведомления об изменениях", callback_data="toggle_notif_changes")],
        [InlineKeyboardButton(text="🔔 Уведомления о новом расписании", callback_data="toggle_notif_schedule")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Simple back button keyboard"""
    keyboard = [[KeyboardButton(text="◀️ Назад")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
