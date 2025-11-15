import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import Database
from parser.parser import run_initial_parsing, check_and_notify_schedule_changes
from notifications import NotificationService
from aiogram import Bot

def setup_scheduler(db: Database, bot: Bot = None):
    """
    Setup scheduler for automated tasks
    
    Args:
        db: Database instance
        bot: Bot instance (optional, required for notifications)
    """
    scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")
    
    # Check for schedule updates every 30 minutes
    scheduler.add_job(
        check_and_notify_schedule_changes, 
        'interval', 
        minutes=30, 
        args=(db, bot), 
        name="Schedule Check and Notify"
    )
    
    # Send morning reminders at 7:30 AM
    if bot:
        notification_service = NotificationService(db, bot)
        scheduler.add_job(
            send_morning_reminders,
            'cron',
            hour=7,
            minute=30,
            args=(db, notification_service),
            name="Morning Reminders"
        )
        logging.info("Morning reminder scheduler configured for 07:30")
    
    logging.info("Scheduler has been configured.")
    return scheduler

async def send_morning_reminders(db: Database, notification_service: NotificationService):
    """Send morning reminders to all users who have them enabled"""
    try:
        users = await db.get_users_for_morning_reminder()
        logging.info(f"Sending morning reminders to {len(users) if users else 0} users")
        
        if not users:
            return
        
        for user_id, group_name, reminder_time in users:
            if group_name:  # Only send if user has selected a group
                await notification_service.send_morning_reminder(user_id, group_name)
        
        logging.info("Morning reminders sent successfully")
    except Exception as e:
        logging.error(f"Error sending morning reminders: {e}", exc_info=True)