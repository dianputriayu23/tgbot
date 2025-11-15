from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_education_form_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="9 классов", callback_data="register:form:9_classes")
    builder.button(text="11 классов", callback_data="register:form:11_classes")
    return builder.as_markup()

def get_course_kb(education_form):
    builder = InlineKeyboardBuilder()
    courses = range(1, 5) if education_form == '9_classes' else range(1, 4)
    for course in courses:
        builder.button(text=f"{course} курс", callback_data=f"register:course:{course}")
    builder.button(text="« Назад", callback_data="register_start")
    builder.adjust(2)
    return builder.as_markup()

def get_group_kb(groups, education_form):
    builder = InlineKeyboardBuilder()
    for group in groups:
        builder.button(text=group, callback_data=f"register:group:{group}")
    builder.button(text="« Назад", callback_data=f"register:course_back:{education_form}")
    builder.adjust(2)
    return builder.as_markup()

def get_settings_kb(user_data):
    builder = InlineKeyboardBuilder()
    notify_schedule_text = "✅ Уведомления о расписании" if user_data[6] else "❌ Уведомления о расписании"
    notify_changes_text = "✅ Уведомления об изменениях" if user_data[7] else "❌ Уведомления об изменениях"
    
    builder.button(text="Сменить группу", callback_data="settings:change_group")
    builder.button(text=notify_schedule_text, callback_data="settings:toggle_schedule")
    builder.button(text=notify_changes_text, callback_data="settings:toggle_changes")
    builder.adjust(1)
    return builder.as_markup()