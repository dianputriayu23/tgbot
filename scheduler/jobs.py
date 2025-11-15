import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import Database
from parser.parser import run_initial_parsing

def setup_scheduler(db: Database):
    scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")
    
    # Проверка расписания каждые 20 минут
    scheduler.add_job(run_initial_parsing, 'interval', minutes=20, args=(db,), name="Schedule Check")
    
    # TODO: Добавить уведомления в 7:30 для 1,3 курса и в 10:00 для 2 курса
    # scheduler.add_job(send_daily_notifications, 'cron', hour=7, minute=30, args=(db, [1, 3]), name="Morning Notifications")
    # scheduler.add_job(send_daily_notifications, 'cron', hour=10, minute=0, args=(db, [2]), name="Late Morning Notifications")
    
    logging.info("Scheduler has been configured.")
    return scheduler