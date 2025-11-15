import logging
from aiogram import Router, F
from aiogram.types import Message

from database.db import Database
from keyboards.main import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, db: Database):
    """Show user profile"""
    user = db.get_user(message.from_user.id)
    
    if not user:
        await message.answer(
            "❌ Сначала настройте бота с помощью команды /start",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Format notification statuses
    notif_pairs = "✅ Включены" if user.get('notifications_pairs', 1) else "❌ Выключены"
    notif_changes = "✅ Включены" if user.get('notifications_changes', 1) else "❌ Выключены"
    notif_schedule = "✅ Включены" if user.get('notifications_schedule', 1) else "❌ Выключены"
    
    # Format education base
    base_text = f"База {user.get('education_base', 'не указана')} классов" if user.get('education_base') else "не указана"
    
    profile_text = (
        "👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"👥 Группа: <b>{user.get('group_name', 'не выбрана')}</b>\n"
        f"📚 Курс: <b>{user.get('course', 'не выбран')}</b>\n"
        f"🎓 База: <b>{base_text}</b>\n\n"
        f"<b>Уведомления:</b>\n"
        f"🔔 О парах: {notif_pairs}\n"
        f"🔔 Об изменениях: {notif_changes}\n"
        f"🔔 О новом расписании: {notif_schedule}\n"
    )
    
    await message.answer(
        profile_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
