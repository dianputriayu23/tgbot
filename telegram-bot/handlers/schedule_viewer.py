from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, timedelta
from database.db import Database

router = Router()

DAYS_MAP = {
    "сегодня": 0, "завтра": 1,
    "понедельник": 0, "вторник": 1, "среда": 2,
    "четверг": 3, "пятница": 4, "суббота": 5
}
DAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

async def format_schedule(lessons):
    if not lessons: return "На этот день пар нет 🎉"
    
    date = lessons[0][3]
    day_of_week_ru = lessons[0][2].capitalize()
    header = f"<b>🗓 {day_of_week_ru} ({date})</b>\n\n"
    
    schedule_text = ""
    for lesson in lessons:
        lesson_num = lesson[4]
        time_start = lesson[5]
        time_end = lesson[6]
        subject = lesson[7]
        teacher = lesson[8]
        cabinet = lesson[9]
        
        schedule_text += f"<b>{lesson_num} пара ({time_start} - {time_end})</b>\n"
        schedule_text += f"🔹 <b>{subject}</b>\n"
        if teacher: schedule_text += f"👤 {teacher}\n"
        if cabinet: schedule_text += f"🚪 {cabinet}\n\n"
        
    return header + schedule_text

@router.message(F.text.lower().in_(DAYS_MAP.keys()))
async def get_schedule(message: Message, db: Database):
    user = await db.get_user(message.from_user.id)
    if not user or not user[5]:
        await message.answer("Сначала выбери свою группу. Нажми /start")
        return

    day_query = message.text.lower()
    
    if day_query in ["сегодня", "завтра"]:
        target_date = datetime.now() + timedelta(days=DAYS_MAP[day_query])
        weekday_index = target_date.weekday()
        if weekday_index == 6: # Если воскресенье
            await message.answer("В воскресенье пар нет 😉")
            return
        target_day_name = DAYS_RU[weekday_index]
    else:
        target_day_name = day_query

    lessons = await db.get_schedule_for_group(user[5], target_day_name)
    schedule_message = await format_schedule(lessons)
    await message.answer(schedule_message)