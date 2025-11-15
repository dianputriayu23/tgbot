"""
Schedule handler - displays daily and weekly schedules
"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message

from database import Database
from keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router()


def setup_handlers(db: Database):
    """Setup schedule handlers with database dependency"""
    
    @router.message(F.text == "📅 Расписание на сегодня")
    async def show_today_schedule(message: Message):
        """Show schedule for today"""
        try:
            user = await db.get_user(message.from_user.id)
            
            if not user or not user.get('group_name'):
                await message.answer(
                    "❌ Сначала нужно выбрать группу.\n"
                    "Используйте команду /start для регистрации."
                )
                return
            
            today = datetime.now().strftime('%Y-%m-%d')
            schedule = await db.get_schedule(user['group_name'], today)
            
            if not schedule:
                await message.answer(
                    f"📅 Расписание на сегодня ({datetime.now().strftime('%d.%m.%Y')})\n"
                    f"Группа: {user['group_name']}\n\n"
                    f"📭 На сегодня нет занятий или расписание еще не загружено.",
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Format schedule
            text = f"📅 Расписание на сегодня ({datetime.now().strftime('%d.%m.%Y')})\n"
            text += f"Группа: {user['group_name']}\n"
            
            if schedule[0].get('day_of_week'):
                text += f"День: {schedule[0]['day_of_week']}\n"
            
            text += "\n"
            
            for lesson in schedule:
                text += f"▫️ Пара {lesson['lesson_number']}\n"
                
                if lesson.get('subject'):
                    text += f"  📚 {lesson['subject']}\n"
                
                if lesson.get('teacher'):
                    text += f"  👨‍🏫 {lesson['teacher']}\n"
                
                if lesson.get('room'):
                    text += f"  🚪 Кабинет: {lesson['room']}\n"
                
                text += "\n"
            
            await message.answer(text, reply_markup=get_main_keyboard())
            
        except Exception as e:
            logger.error(f"Error showing today's schedule: {e}")
            await message.answer(
                "❌ Ошибка при получении расписания.",
                reply_markup=get_main_keyboard()
            )
    
    @router.message(F.text == "📆 Расписание на неделю")
    async def show_week_schedule(message: Message):
        """Show schedule for the week"""
        try:
            user = await db.get_user(message.from_user.id)
            
            if not user or not user.get('group_name'):
                await message.answer(
                    "❌ Сначала нужно выбрать группу.\n"
                    "Используйте команду /start для регистрации."
                )
                return
            
            # Get current week (Monday to Sunday)
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            
            start_date = monday.strftime('%Y-%m-%d')
            end_date = sunday.strftime('%Y-%m-%d')
            
            schedule = await db.get_week_schedule(user['group_name'], start_date, end_date)
            
            if not schedule:
                await message.answer(
                    f"📆 Расписание на неделю\n"
                    f"({monday.strftime('%d.%m.%Y')} - {sunday.strftime('%d.%m.%Y')})\n"
                    f"Группа: {user['group_name']}\n\n"
                    f"📭 На эту неделю нет занятий или расписание еще не загружено.",
                    reply_markup=get_main_keyboard()
                )
                return
            
            # Group schedule by date
            schedule_by_date = {}
            for lesson in schedule:
                date = lesson['date']
                if date not in schedule_by_date:
                    schedule_by_date[date] = []
                schedule_by_date[date].append(lesson)
            
            # Format schedule
            text = f"📆 Расписание на неделю\n"
            text += f"({monday.strftime('%d.%m.%Y')} - {sunday.strftime('%d.%m.%Y')})\n"
            text += f"Группа: {user['group_name']}\n\n"
            
            for date_str in sorted(schedule_by_date.keys()):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                lessons = schedule_by_date[date_str]
                
                day_name = lessons[0].get('day_of_week', '')
                text += f"━━━━━━━━━━━━━━━━━━━\n"
                text += f"📅 {date_obj.strftime('%d.%m.%Y')}"
                if day_name:
                    text += f" ({day_name})"
                text += "\n\n"
                
                for lesson in lessons:
                    text += f"▫️ Пара {lesson['lesson_number']}\n"
                    
                    if lesson.get('subject'):
                        text += f"  📚 {lesson['subject']}\n"
                    
                    if lesson.get('teacher'):
                        text += f"  👨‍🏫 {lesson['teacher']}\n"
                    
                    if lesson.get('room'):
                        text += f"  🚪 {lesson['room']}\n"
                    
                    text += "\n"
            
            # Split into multiple messages if too long
            if len(text) > 4000:
                # Send in chunks
                chunks = []
                current_chunk = ""
                
                for line in text.split('\n'):
                    if len(current_chunk) + len(line) + 1 > 4000:
                        chunks.append(current_chunk)
                        current_chunk = line + '\n'
                    else:
                        current_chunk += line + '\n'
                
                if current_chunk:
                    chunks.append(current_chunk)
                
                for i, chunk in enumerate(chunks):
                    if i == len(chunks) - 1:
                        await message.answer(chunk, reply_markup=get_main_keyboard())
                    else:
                        await message.answer(chunk)
            else:
                await message.answer(text, reply_markup=get_main_keyboard())
            
        except Exception as e:
            logger.error(f"Error showing week schedule: {e}")
            await message.answer(
                "❌ Ошибка при получении расписания.",
                reply_markup=get_main_keyboard()
            )
    
    return router
