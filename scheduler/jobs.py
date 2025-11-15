import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import Database
from parser.parser import run_initial_parsing

def setup_scheduler(db: Database):
    scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")
    scheduler.add_job(run_initial_parsing, 'interval', minutes=30, args=(db,), name="Schedule Check")
    logging.info("Scheduler has been configured.")
    return scheduler