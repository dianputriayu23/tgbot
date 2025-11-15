"""
Settings handler.
Handles user settings and preferences.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from database import Database
from keyboards import get_notifications_keyboard, get_time_keyboard, get_course_keyboard, get_group_keyboard
from handlers.start import GROUPS

logger = logging.getLogger(__name__)


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle "Настройки" button.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    user_id = update.effective_user.id
    db: Database = context.bot_data['db']
    
    # Get user data
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(
            "❌ Сначала настройте бота с помощью /start"
        )
        return
    
    # Display settings
    message = "⚙️ Настройки\n\n"
    
    if user_data.get('group_name'):
        message += f"📚 Курс: {user_data.get('course', 'Не указан')}\n"
        message += f"👥 Группа: {user_data['group_name']}\n\n"
    else:
        message += "📚 Группа: Не настроена\n\n"
    
    notif_status = "✅ Включены" if user_data.get('notifications_enabled', 1) else "❌ Выключены"
    notif_time = user_data.get('notification_time', '08:00')
    
    message += f"🔔 Уведомления: {notif_status}\n"
    message += f"⏰ Время уведомлений: {notif_time}\n\n"
    
    message += "Выберите что изменить:\n"
    message += "/changegroup - Изменить группу\n"
    message += "/notifications - Настроить уведомления"
    
    await update.message.reply_text(message)


async def notifications_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /notifications command.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    user_id = update.effective_user.id
    db: Database = context.bot_data['db']
    
    user_data = await db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(
            "❌ Сначала настройте бота с помощью /start"
        )
        return
    
    notif_status = "включены" if user_data.get('notifications_enabled', 1) else "выключены"
    notif_time = user_data.get('notification_time', '08:00')
    
    await update.message.reply_text(
        f"🔔 Уведомления о расписании\n\n"
        f"Статус: {notif_status}\n"
        f"Время: {notif_time}\n\n"
        "Что вы хотите сделать?",
        reply_markup=get_notifications_keyboard()
    )


async def notification_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle notification enable/disable.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db: Database = context.bot_data['db']
    
    action = query.data.replace('notif_', '')
    
    if action == 'on':
        await db.update_notifications(user_id, True)
        await query.edit_message_text(
            "✅ Уведомления включены!\n\n"
            "Вы будете получать расписание каждый день в установленное время."
        )
        logger.info(f"User {user_id} enabled notifications")
    
    elif action == 'off':
        await db.update_notifications(user_id, False)
        await query.edit_message_text(
            "❌ Уведомления выключены.\n\n"
            "Вы можете включить их снова в любое время."
        )
        logger.info(f"User {user_id} disabled notifications")
    
    elif action == 'time':
        await query.edit_message_text(
            "⏰ Выберите время для получения уведомлений:"
        )
        await query.message.reply_text(
            "Выберите время или введите в формате ЧЧ:ММ (например, 08:30):",
            reply_markup=get_time_keyboard()
        )
        context.user_data['awaiting_time'] = True


async def time_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle time input from user.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    if not context.user_data.get('awaiting_time'):
        return
    
    time_text = update.message.text.strip()
    
    if time_text == "❌ Отмена":
        context.user_data['awaiting_time'] = False
        await update.message.reply_text("Отменено")
        return
    
    # Validate time format
    import re
    if not re.match(r'^\d{1,2}:\d{2}$', time_text):
        await update.message.reply_text(
            "❌ Неверный формат времени.\n"
            "Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30)"
        )
        return
    
    try:
        hours, minutes = map(int, time_text.split(':'))
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError
        
        user_id = update.effective_user.id
        db: Database = context.bot_data['db']
        
        await db.update_notifications(user_id, True, time_text)
        
        await update.message.reply_text(
            f"✅ Время уведомлений установлено: {time_text}\n\n"
            "Вы будете получать расписание каждый день в это время."
        )
        
        context.user_data['awaiting_time'] = False
        logger.info(f"User {user_id} set notification time to {time_text}")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверное время.\n"
            "Часы должны быть от 0 до 23, минуты от 0 до 59."
        )


async def change_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /changegroup command.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    await update.message.reply_text(
        "Выберите ваш курс:",
        reply_markup=get_course_keyboard()
    )
    context.user_data['changing_group'] = True


async def change_course_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle course selection when changing group.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    if not context.user_data.get('changing_group'):
        return
    
    query = update.callback_query
    await query.answer()
    
    # Extract course number
    course = int(query.data.split('_')[1])
    context.user_data['new_course'] = course
    
    # Get groups for this course
    groups = GROUPS.get(course, [])
    
    if not groups:
        await query.edit_message_text(
            "Извините, для этого курса нет доступных групп."
        )
        context.user_data['changing_group'] = False
        return
    
    await query.edit_message_text(
        f"Выбран {course} курс.\n\n"
        "Теперь выберите вашу группу:",
        reply_markup=get_group_keyboard(groups)
    )


async def change_group_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle group selection when changing group.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    if not context.user_data.get('changing_group'):
        return
    
    query = update.callback_query
    await query.answer()
    
    # Extract group name
    group_name = query.data.replace('group_', '')
    course = context.user_data.get('new_course', 1)
    
    # Save to database
    db: Database = context.bot_data['db']
    await db.update_user_group(query.from_user.id, course, group_name)
    
    await query.edit_message_text(
        f"✅ Группа изменена!\n\n"
        f"Курс: {course}\n"
        f"Группа: {group_name}"
    )
    
    context.user_data['changing_group'] = False
    logger.info(f"User {query.from_user.id} changed group to {group_name}")
