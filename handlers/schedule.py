import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message

from database.db import Database
from keyboards.main import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router()

# Emoji for lessons
EMOJI_MAP = {
    "book": "📚",
    "time": "🕐",
    "teacher": "👨‍🏫",
    "room": "🚪",
    "warning": "⚠️"
}

# Weekday mapping
WEEKDAYS_RU = {
    0: "Понедельник",
    1: "Вторник", 
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

WEEKDAYS_SHORT = {
    "Пн": 0,
    "Вт": 1,
    "Ср": 2,
    "Чт": 3,
    "Пт": 4,
    "Сб": 5
}


@router.message(F.text == "📅 Сегодня")
async def show_today_schedule(message: Message, db: Database):
    """Show today's schedule"""
    user = db.get_user(message.from_user.id)
    
    if not user or not user.get('group_name'):
        await message.answer(
            "❌ Сначала выберите группу с помощью команды /start",
            reply_markup=get_main_keyboard()
        )
        return
    
    today = datetime.now()
    weekday_name = WEEKDAYS_RU[today.weekday()]
    
    await send_schedule_for_day(message, user, weekday_name, "Сегодня")


@router.message(F.text == "📆 Завтра")
async def show_tomorrow_schedule(message: Message, db: Database):
    """Show tomorrow's schedule"""
    user = db.get_user(message.from_user.id)
    
    if not user or not user.get('group_name'):
        await message.answer(
            "❌ Сначала выберите группу с помощью команды /start",
            reply_markup=get_main_keyboard()
        )
        return
    
    tomorrow = datetime.now() + timedelta(days=1)
    weekday_name = WEEKDAYS_RU[tomorrow.weekday()]
    
    await send_schedule_for_day(message, user, weekday_name, "Завтра")


@router.message(F.text.in_(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]))
async def show_weekday_schedule(message: Message, db: Database):
    """Show schedule for specific weekday"""
    user = db.get_user(message.from_user.id)
    
    if not user or not user.get('group_name'):
        await message.answer(
            "❌ Сначала выберите группу с помощью команды /start",
            reply_markup=get_main_keyboard()
        )
        return
    
    weekday_idx = WEEKDAYS_SHORT[message.text]
    weekday_name = WEEKDAYS_RU[weekday_idx]
    
    await send_schedule_for_day(message, user, weekday_name, weekday_name)


async def send_schedule_for_day(message: Message, user: dict, weekday_name: str, title: str):
    """Send formatted schedule for a specific day"""
    group_name = user['group_name']
    
    # TODO: Get actual schedule from database/parser
    # For now, show a placeholder message
    
    schedule_text = f"📅 <b>{title} ({weekday_name})</b>\n"
    schedule_text += f"👥 Группа: <b>{group_name}</b>\n\n"
    
    # Mock schedule data - in real implementation, get from DB
    has_lessons = False  # This would be determined by actual data
    
    if has_lessons:
        schedule_text += f"{EMOJI_MAP['time']} <b>12:30-13:50</b> (III пара)\n"
        schedule_text += f"{EMOJI_MAP['book']} История России\n"
        schedule_text += f"{EMOJI_MAP['teacher']} Иванов И.И.\n"
        schedule_text += f"{EMOJI_MAP['room']} Кабинет 301\n\n"
    else:
        schedule_text += f"{EMOJI_MAP['warning']} Пар нет, проверьте на сайте https://pkeu.ru\n\n"
        schedule_text += "Возможно, расписание еще не загружено или это выходной день."
    
    await message.answer(
        schedule_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


def format_lesson(lesson_data: dict) -> str:
    """Format lesson data into readable text"""
    text = ""
    
    if "time" in lesson_data:
        text += f"{EMOJI_MAP['time']} <b>{lesson_data['time']}</b>\n"
    
    if "subject" in lesson_data:
        text += f"{EMOJI_MAP['book']} {lesson_data['subject']}\n"
    
    if "teacher" in lesson_data:
        text += f"{EMOJI_MAP['teacher']} {lesson_data['teacher']}\n"
    
    if "room" in lesson_data:
        text += f"{EMOJI_MAP['room']} Кабинет {lesson_data['room']}\n"
    
    return text
