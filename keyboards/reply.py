from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Сегодня")
    builder.button(text="Завтра")
    builder.button(text="Понедельник")
    builder.button(text="Вторник")
    builder.button(text="Среда")
    builder.button(text="Четверг")
    builder.button(text="Пятница")
    builder.button(text="Суббота")
    builder.button(text="⚙️ Настройки")
    builder.button(text="❓ Помощь")
    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup(resize_keyboard=True)