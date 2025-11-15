"""
Start command handler.
Handles /start command and initial user setup.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from database import Database
from keyboards import get_main_keyboard, get_course_keyboard, get_group_keyboard

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_COURSE, SELECTING_GROUP = range(2)

# Sample groups for each course (should be dynamically loaded from schedule)
GROUPS = {
    1: ["БУ-25", "Ф-25", "ТД-25", "Ю-25"],
    2: ["БУ1-24", "Ф1-24", "БД1-24", "ТД1-24", "Ю1-24(1)", "Ю1-24(2)", "Ю1-24(3)"],
    3: ["БУ-23", "Ф-23", "ТД-23", "Ю-23"],
    4: ["БУ-22", "Ф-22", "ТД-22", "Ю-22"]
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command.
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        Next conversation state
    """
    user = update.effective_user
    db: Database = context.bot_data['db']
    
    # Add user to database
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Check if user already has a group
    user_data = await db.get_user(user.id)
    
    if user_data and user_data.get('group_name'):
        # User already configured
        await update.message.reply_text(
            f"С возвращением, {user.first_name}! 👋\n\n"
            f"Ваша группа: {user_data['group_name']}\n\n"
            "Используйте меню ниже для навигации.",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    # New user - start setup
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для расписания колледжа.\n\n"
        "Для начала работы, пожалуйста, выберите ваш курс:"
    )
    
    await update.message.reply_text(
        "На каком курсе вы учитесь?",
        reply_markup=get_course_keyboard()
    )
    
    return SELECTING_COURSE


async def course_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle course selection.
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()
    
    # Extract course number
    course = int(query.data.split('_')[1])
    context.user_data['course'] = course
    
    logger.info(f"User {query.from_user.id} selected course {course}")
    
    # Get groups for this course
    groups = GROUPS.get(course, [])
    
    if not groups:
        await query.edit_message_text(
            "Извините, для этого курса нет доступных групп.\n"
            "Пожалуйста, свяжитесь с администратором."
        )
        return ConversationHandler.END
    
    await query.edit_message_text(
        f"Отлично! Вы выбрали {course} курс.\n\n"
        "Теперь выберите вашу группу:",
        reply_markup=get_group_keyboard(groups)
    )
    
    return SELECTING_GROUP


async def group_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle group selection.
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        End conversation
    """
    query = update.callback_query
    await query.answer()
    
    # Extract group name
    group_name = query.data.replace('group_', '')
    course = context.user_data.get('course', 1)
    
    logger.info(f"User {query.from_user.id} selected group {group_name}")
    
    # Save to database
    db: Database = context.bot_data['db']
    await db.update_user_group(query.from_user.id, course, group_name)
    
    await query.edit_message_text(
        f"✅ Настройка завершена!\n\n"
        f"Курс: {course}\n"
        f"Группа: {group_name}\n\n"
        "Используйте меню ниже для просмотра расписания."
    )
    
    await query.message.reply_text(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )
    
    return ConversationHandler.END


async def back_to_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle back button - return to course selection.
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        Previous conversation state
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "На каком курсе вы учитесь?",
        reply_markup=get_course_keyboard()
    )
    
    return SELECTING_COURSE


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the setup conversation.
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        End conversation
    """
    await update.message.reply_text(
        "Настройка отменена. Вы можете начать заново командой /start"
    )
    
    return ConversationHandler.END


# Create conversation handler for initial setup
def get_start_conversation_handler():
    """
    Get conversation handler for initial user setup.
    
    Returns:
        ConversationHandler instance
    """
    return ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            SELECTING_COURSE: [
                CallbackQueryHandler(course_selected, pattern=r'^course_\d+$')
            ],
            SELECTING_GROUP: [
                CallbackQueryHandler(group_selected, pattern=r'^group_.+$'),
                CallbackQueryHandler(back_to_course, pattern=r'^back_to_course$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_setup)],
        allow_reentry=True
    )
