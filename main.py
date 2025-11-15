import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from database.db import Database
from parser.parser import ScheduleParser
from scheduler.jobs import SchedulerJobs

# Import handlers
from handlers import start, schedule, settings, profile, help as help_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    schedule_url = os.getenv('SCHEDULE_URL', 'https://pkeu.ru/sites/default/files/Files_up_page/')
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Initialize database
    db = Database()
    
    # Initialize parser
    parser = ScheduleParser(schedule_url)
    
    # Initialize scheduler
    scheduler = SchedulerJobs(bot, db, parser)
    
    # Register middleware to pass db to handlers
    @dp.update.middleware()
    async def db_middleware(handler, event, data):
        data['db'] = db
        return await handler(event, data)
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(schedule.router)
    dp.include_router(settings.router)
    dp.include_router(profile.router)
    dp.include_router(help_handler.router)
    
    # Start scheduler
    scheduler.start()
    
    logger.info("Bot started successfully!")
    
    try:
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Cleanup
        scheduler.stop()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
