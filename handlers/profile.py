"""
Profile handler - shows user profile information
"""
import logging
from aiogram import Router, F
from aiogram.types import Message

from database import Database
from keyboards import get_main_keyboard

logger = logging.getLogger(__name__)

router = Router()


def setup_handlers(db: Database):
    """Setup profile handlers with database dependency"""
    
    @router.message(F.text == "👤 Профиль")
    async def show_profile(message: Message):
        """Show user profile"""
        try:
            user = await db.get_user(message.from_user.id)
            
            if not user:
                await message.answer(
                    "❌ Профиль не найден.\n"
                    "Используйте команду /start для регистрации."
                )
                return
            
            # Format profile information
            text = "👤 Ваш профиль\n\n"
            
            if user.get('first_name'):
                text += f"Имя: {user['first_name']}"
                if user.get('last_name'):
                    text += f" {user['last_name']}"
                text += "\n"
            
            if user.get('username'):
                text += f"Username: @{user['username']}\n"
            
            text += f"\n📚 Учебная информация:\n"
            
            if user.get('group_name'):
                text += f"Группа: {user['group_name']}\n"
                text += f"База: {user['base']} классов\n"
                text += f"Курс: {user['course']}\n"
            else:
                text += "❌ Группа не выбрана\n"
                text += "Используйте /start для выбора группы\n"
            
            text += f"\n🔔 Настройки:\n"
            notifications_status = "включены ✅" if user.get('notifications_enabled', 1) else "выключены ❌"
            text += f"Уведомления: {notifications_status}\n"
            
            await message.answer(text, reply_markup=get_main_keyboard())
            
        except Exception as e:
            logger.error(f"Error showing profile: {e}")
            await message.answer(
                "❌ Ошибка при получении профиля.",
                reply_markup=get_main_keyboard()
            )
    
    return router
