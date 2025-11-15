"""
Schedule display handler.
Handles schedule viewing and formatting.
"""

import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from database import Database
from keyboards import get_schedule_period_keyboard

logger = logging.getLogger(__name__)


async def my_schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle "Моё расписание" button.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    user_id = update.effective_user.id
    db: Database = context.bot_data['db']
    
    # Get user data
    user_data = await db.get_user(user_id)
    
    if not user_data or not user_data.get('group_name'):
        await update.message.reply_text(
            "❌ Сначала настройте вашу группу с помощью /start"
        )
        return
    
    group_name = user_data['group_name']
    
    # Show period selection
    await update.message.reply_text(
        f"📅 Расписание для группы {group_name}\n\n"
        "Выберите период:",
        reply_markup=get_schedule_period_keyboard()
    )


async def schedule_by_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle "Расписание на дату" button.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    user_id = update.effective_user.id
    db: Database = context.bot_data['db']
    
    # Get user data
    user_data = await db.get_user(user_id)
    
    if not user_data or not user_data.get('group_name'):
        await update.message.reply_text(
            "❌ Сначала настройте вашу группу с помощью /start"
        )
        return
    
    await update.message.reply_text(
        "📆 Введите дату в формате ДД.ММ.ГГГГ\n"
        "Например: 15.11.2025"
    )
    
    context.user_data['awaiting_date'] = True


async def period_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle period selection callback.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db: Database = context.bot_data['db']
    
    # Get user data
    user_data = await db.get_user(user_id)
    if not user_data or not user_data.get('group_name'):
        await query.edit_message_text("❌ Группа не настроена")
        return
    
    group_name = user_data['group_name']
    period = query.data.replace('period_', '')
    
    # Determine date range based on period
    today = datetime.now().date()
    
    if period == 'today':
        date_str = today.strftime('%Y-%m-%d')
        await show_schedule_for_date(query, db, group_name, date_str, "Сегодня")
    
    elif period == 'tomorrow':
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime('%Y-%m-%d')
        await show_schedule_for_date(query, db, group_name, date_str, "Завтра")
    
    elif period == 'week':
        await show_schedule_for_week(query, db, group_name, today, "Эта неделя")
    
    elif period == 'next_week':
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        await show_schedule_for_week(query, db, group_name, next_week_start, "Следующая неделя")
    
    elif period == 'custom':
        await query.edit_message_text(
            "📆 Введите дату в формате ДД.ММ.ГГГГ\n"
            "Например: 15.11.2025"
        )
        context.user_data['awaiting_date'] = True


async def show_schedule_for_date(query, db: Database, group_name: str, 
                                 date_str: str, period_name: str):
    """
    Show schedule for a specific date.
    
    Args:
        query: Callback query
        db: Database instance
        group_name: Group name
        date_str: Date in YYYY-MM-DD format
        period_name: Display name for the period
    """
    schedule = await db.get_schedule_for_group(group_name, date_str)
    
    if not schedule:
        await query.edit_message_text(
            f"📅 {period_name} ({date_str})\n\n"
            f"Группа: {group_name}\n\n"
            "📝 Расписание пока не загружено или нет занятий"
        )
        return
    
    # Format schedule
    message = f"📅 {period_name} ({date_str})\n"
    message += f"Группа: {group_name}\n"
    message += f"День: {schedule[0]['day_of_week'].title()}\n\n"
    
    for entry in schedule:
        message += f"⏰ {entry['time_slot']}\n"
        message += f"📚 {entry['subject']}\n"
        
        if entry['teacher']:
            message += f"👨‍🏫 {entry['teacher']}\n"
        
        if entry['room']:
            message += f"🏫 Аудитория: {entry['room']}\n"
        
        message += "\n"
    
    # Split if too long
    if len(message) > 4000:
        parts = split_message(message)
        await query.edit_message_text(parts[0])
        for part in parts[1:]:
            await query.message.reply_text(part)
    else:
        await query.edit_message_text(message)


async def show_schedule_for_week(query, db: Database, group_name: str, 
                                 start_date: datetime.date, period_name: str):
    """
    Show schedule for a week.
    
    Args:
        query: Callback query
        db: Database instance
        group_name: Group name
        start_date: Start date of the week
        period_name: Display name for the period
    """
    message = f"📅 {period_name}\n"
    message += f"Группа: {group_name}\n\n"
    
    has_schedule = False
    
    # Get schedule for each day of the week
    for i in range(7):
        date = start_date + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        schedule = await db.get_schedule_for_group(group_name, date_str)
        
        if schedule:
            has_schedule = True
            day_name = schedule[0]['day_of_week'].title()
            message += f"━━━━━━━━━━━━━━━\n"
            message += f"📆 {day_name} ({date.strftime('%d.%m')})\n\n"
            
            for entry in schedule:
                message += f"⏰ {entry['time_slot']}\n"
                message += f"📚 {entry['subject']}\n"
                
                if entry['room']:
                    message += f"🏫 {entry['room']}"
                    if entry['teacher']:
                        message += f" • 👨‍🏫 {entry['teacher']}"
                    message += "\n"
                elif entry['teacher']:
                    message += f"👨‍🏫 {entry['teacher']}\n"
                
                message += "\n"
    
    if not has_schedule:
        message += "📝 Расписание пока не загружено"
    
    # Split if too long
    if len(message) > 4000:
        parts = split_message(message)
        await query.edit_message_text(parts[0])
        for part in parts[1:]:
            await query.message.reply_text(part)
    else:
        await query.edit_message_text(message)


async def date_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle date input from user.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    if not context.user_data.get('awaiting_date'):
        return
    
    date_text = update.message.text.strip()
    
    # Try to parse date
    try:
        date = datetime.strptime(date_text, '%d.%m.%Y').date()
        date_str = date.strftime('%Y-%m-%d')
        
        user_id = update.effective_user.id
        db: Database = context.bot_data['db']
        user_data = await db.get_user(user_id)
        
        if not user_data or not user_data.get('group_name'):
            await update.message.reply_text("❌ Группа не настроена")
            return
        
        group_name = user_data['group_name']
        schedule = await db.get_schedule_for_group(group_name, date_str)
        
        if not schedule:
            await update.message.reply_text(
                f"📅 {date_text}\n\n"
                f"Группа: {group_name}\n\n"
                "📝 Расписание пока не загружено или нет занятий"
            )
        else:
            # Format schedule
            message = f"📅 {date_text}\n"
            message += f"Группа: {group_name}\n"
            message += f"День: {schedule[0]['day_of_week'].title()}\n\n"
            
            for entry in schedule:
                message += f"⏰ {entry['time_slot']}\n"
                message += f"📚 {entry['subject']}\n"
                
                if entry['teacher']:
                    message += f"👨‍🏫 {entry['teacher']}\n"
                
                if entry['room']:
                    message += f"🏫 Аудитория: {entry['room']}\n"
                
                message += "\n"
            
            await update.message.reply_text(message)
        
        context.user_data['awaiting_date'] = False
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты.\n"
            "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n"
            "Например: 15.11.2025"
        )


def split_message(message: str, max_length: int = 4000) -> list:
    """
    Split a long message into multiple parts.
    
    Args:
        message: Message to split
        max_length: Maximum length of each part
        
    Returns:
        List of message parts
    """
    if len(message) <= max_length:
        return [message]
    
    parts = []
    lines = message.split('\n')
    current_part = ""
    
    for line in lines:
        if len(current_part) + len(line) + 1 > max_length:
            parts.append(current_part)
            current_part = line + "\n"
        else:
            current_part += line + "\n"
    
    if current_part:
        parts.append(current_part)
    
    return parts
