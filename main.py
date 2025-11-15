"""
Main entry point for the Telegram bot.
Handles bot initialization, configuration, and startup.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Import modules
from database import Database
from parser import ScheduleParser
from scheduler import ScheduleJobManager
from handlers import (
    get_start_conversation_handler,
    my_schedule_handler,
    schedule_by_date_handler,
    period_selected,
    date_input_handler,
    settings_handler,
    notifications_settings,
    notification_toggle,
    time_input_handler,
    change_group_handler,
    change_course_selected,
    change_group_selected,
    profile_handler,
    help_handler,
    about_handler
)

# Configure logging
def setup_logging():
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Set specific log levels
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)


async def post_init(application: Application) -> None:
    """
    Post-initialization hook.
    
    Args:
        application: The application instance
    """
    logger = logging.getLogger(__name__)
    
    # Initialize database
    db: Database = application.bot_data['db']
    await db.connect()
    await db.initialize()
    logger.info("Database initialized")
    
    # Initialize scheduler
    scheduler: ScheduleJobManager = application.bot_data['scheduler']
    
    # Do initial schedule update
    logger.info("Performing initial schedule update...")
    await scheduler.update_schedule_cache()
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")


async def post_shutdown(application: Application) -> None:
    """
    Post-shutdown hook.
    
    Args:
        application: The application instance
    """
    logger = logging.getLogger(__name__)
    
    # Stop scheduler
    scheduler: ScheduleJobManager = application.bot_data['scheduler']
    scheduler.stop()
    logger.info("Scheduler stopped")
    
    # Close database
    db: Database = application.bot_data['db']
    await db.close()
    logger.info("Database closed")


def main():
    """Main function to run the bot."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Telegram bot...")
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with BOT_TOKEN=your_token_here")
        sys.exit(1)
    
    database_path = os.getenv('DATABASE_PATH', 'schedule.db')
    schedule_folder = os.getenv('SCHEDULE_FOLDER', '.')
    
    logger.info(f"Configuration loaded:")
    logger.info(f"  Database: {database_path}")
    logger.info(f"  Schedule folder: {schedule_folder}")
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Initialize components
    db = Database(database_path)
    parser = ScheduleParser()
    scheduler = ScheduleJobManager(
        bot=application.bot,
        db=db,
        parser=parser,
        schedule_folder=schedule_folder
    )
    
    # Store in bot_data for access in handlers
    application.bot_data['db'] = db
    application.bot_data['parser'] = parser
    application.bot_data['scheduler'] = scheduler
    
    # Add handlers
    
    # Start conversation handler (must be added first)
    application.add_handler(get_start_conversation_handler())
    
    # Command handlers
    application.add_handler(CommandHandler('help', help_handler))
    application.add_handler(CommandHandler('about', about_handler))
    application.add_handler(CommandHandler('notifications', notifications_settings))
    application.add_handler(CommandHandler('changegroup', change_group_handler))
    
    # Callback query handlers (for inline keyboards)
    application.add_handler(CallbackQueryHandler(
        period_selected, 
        pattern=r'^period_.+$'
    ))
    application.add_handler(CallbackQueryHandler(
        notification_toggle, 
        pattern=r'^notif_.+$'
    ))
    application.add_handler(CallbackQueryHandler(
        change_course_selected, 
        pattern=r'^course_\d+$'
    ))
    application.add_handler(CallbackQueryHandler(
        change_group_selected, 
        pattern=r'^group_.+$'
    ))
    
    # Message handlers (for main menu buttons)
    application.add_handler(MessageHandler(
        filters.Regex(r'^📅 Моё расписание$'),
        my_schedule_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^📆 Расписание на дату$'),
        schedule_by_date_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^👤 Профиль$'),
        profile_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^⚙️ Настройки$'),
        settings_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^❓ Помощь$'),
        help_handler
    ))
    
    # Date and time input handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex(r'^[📅📆👤⚙️❓◀️❌]'),
        date_input_handler
    ))
    application.add_handler(MessageHandler(
        filters.Regex(r'^\d{1,2}:\d{2}$'),
        time_input_handler
    ))
    
    # Add hooks
    application.post_init = post_init
    application.post_shutdown = post_shutdown
    
    # Start the bot
    logger.info("Bot is ready! Starting polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
