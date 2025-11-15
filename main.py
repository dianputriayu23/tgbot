import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import Database
from handlers import common, schedule_viewer
from scheduler.jobs import setup_scheduler
from parser.parser import run_initial_parsing, set_bot_instance

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    load_dotenv()

    bot = Bot(token=os.getenv("API_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    db = Database('schedule.db')

    await db.initialize()
    logging.info("Database initialized.")
    
    # Set bot instance for parser notifications
    set_bot_instance(bot)

    dp.include_router(common.router)
    dp.include_router(schedule_viewer.router)
    logging.info("Command handlers registered.")
    
    logging.info("Performing initial schedule check on startup...")
    await run_initial_parsing(db)
    logging.info("Initial check complete.")

    scheduler = setup_scheduler(db, bot)
    scheduler.start()
    logging.info("Scheduler has been started.")

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot is starting polling...")
    await dp.start_polling(bot, db=db)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")