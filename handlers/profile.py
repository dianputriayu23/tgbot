"""
Profile handler.
Handles user profile display.
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from database import Database

logger = logging.getLogger(__name__)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle "Профиль" button.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    user = update.effective_user
    user_id = user.id
    db: Database = context.bot_data['db']
    
    # Get user data
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(
            "❌ Сначала настройте бота с помощью /start"
        )
        return
    
    # Format profile information
    message = "👤 Ваш профиль\n\n"
    
    # Basic info
    message += f"🆔 ID: {user_id}\n"
    
    if user.username:
        message += f"👤 Username: @{user.username}\n"
    
    message += f"📝 Имя: {user.first_name}"
    if user.last_name:
        message += f" {user.last_name}"
    message += "\n\n"
    
    # Study info
    if user_data.get('course'):
        message += f"📚 Курс: {user_data['course']}\n"
    
    if user_data.get('group_name'):
        message += f"👥 Группа: {user_data['group_name']}\n"
    else:
        message += "👥 Группа: Не настроена\n"
    
    message += "\n"
    
    # Notification settings
    if user_data.get('notifications_enabled', 1):
        message += "🔔 Уведомления: ✅ Включены\n"
        message += f"⏰ Время: {user_data.get('notification_time', '08:00')}\n"
    else:
        message += "🔔 Уведомления: ❌ Выключены\n"
    
    message += "\n"
    
    # Account info
    created_at = user_data.get('created_at', '')
    if created_at:
        try:
            # Parse datetime from database
            if isinstance(created_at, str):
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                dt = created_at
            
            message += f"📅 Дата регистрации: {dt.strftime('%d.%m.%Y %H:%M')}\n"
        except:
            pass
    
    message += "\n"
    message += "Используйте /changegroup для изменения группы\n"
    message += "Используйте /notifications для настройки уведомлений"
    
    await update.message.reply_text(message)
    
    logger.info(f"User {user_id} viewed profile")
