"""
Main entry point for the Telegram bot
"""
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database import Database
from handlers import start, schedule, settings, profile, help as help_handler
from scheduler import SchedulerJobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the bot"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not found in environment variables")
            logger.error("Please create a .env file with BOT_TOKEN=your_token_here")
            return
        
        database_path = os.getenv('DATABASE_PATH', 'bot_database.db')
        schedule_dir = os.getenv('SCHEDULE_DIR', '.')
        
        logger.info("Starting Telegram Bot for College Schedule")
        logger.info(f"Database: {database_path}")
        logger.info(f"Schedule directory: {schedule_dir}")
        
        # Initialize database
        db = Database(database_path)
        await db.init_db()
        logger.info("Database initialized")
        
        # Initialize bot and dispatcher
        bot = Bot(
            token=bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Setup handlers
        logger.info("Setting up handlers")
        start_router = start.setup_handlers(db)
        schedule_router = schedule.setup_handlers(db)
        settings_router = settings.setup_handlers(db)
        profile_router = profile.setup_handlers(db)
        help_router = help_handler.setup_handlers()
        
        # Include routers
        dp.include_router(start_router)
        dp.include_router(schedule_router)
        dp.include_router(settings_router)
        dp.include_router(profile_router)
        dp.include_router(help_router)
        
        logger.info("Handlers configured")
        
        # Initialize scheduler
        scheduler = SchedulerJobs(bot, db, schedule_dir)
        scheduler.start()
        logger.info("Scheduler started")
        
        # Start polling
        logger.info("Bot started. Press Ctrl+C to stop.")
        
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            # Cleanup
            scheduler.shutdown()
            await bot.session.close()
            logger.info("Bot stopped")
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
