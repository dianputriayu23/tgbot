import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import Database
from parser.parser import run_initial_parsing

async def send_morning_notification(db: Database, bot, course):
    """Send morning schedule notification for specific course"""
    try:
        from handlers.schedule_viewer import format_schedule, DAYS_RU
        
        users = await db.get_users_for_morning_notification(course)
        if not users:
            return
        
        today = datetime.now()
        weekday_index = today.weekday()
        
        if weekday_index == 6:  # Sunday
            return
        
        day_name = DAYS_RU[weekday_index]
        
        for user_id, group_name in users:
            try:
                lessons = await db.get_schedule_for_group(group_name, day_name)
                schedule_msg = await format_schedule(lessons)
                await bot.send_message(user_id, f"🌅 Доброе утро! Вот твоё расписание на сегодня:\n\n{schedule_msg}")
            except Exception as e:
                logging.error(f"Error sending morning notification to user {user_id}: {e}")
    except Exception as e:
        logging.error(f"Error in morning notification job: {e}")

async def send_evening_notification(db: Database, bot):
    """Send evening schedule notification for tomorrow"""
    try:
        from handlers.schedule_viewer import format_schedule, DAYS_RU
        
        users = await db.get_all_users_for_evening_notification()
        if not users:
            return
        
        tomorrow = datetime.now() + timedelta(days=1)
        weekday_index = tomorrow.weekday()
        
        if weekday_index == 6:  # Sunday
            return
        
        day_name = DAYS_RU[weekday_index]
        
        for user_id, group_name in users:
            try:
                lessons = await db.get_schedule_for_group(group_name, day_name)
                schedule_msg = await format_schedule(lessons)
                await bot.send_message(user_id, f"🌙 Расписание на завтра:\n\n{schedule_msg}")
            except Exception as e:
                logging.error(f"Error sending evening notification to user {user_id}: {e}")
    except Exception as e:
        logging.error(f"Error in evening notification job: {e}")

async def send_change_notification(db: Database, bot, changed_groups):
    """Send notification to users when their schedule changes"""
    if not changed_groups:
        return
    
    try:
        for group_name in changed_groups:
            users = await db.get_users_by_group(group_name)
            if not users:
                continue
            
            message = f"⚠️ <b>Внимание!</b>\n\nВ расписании группы <b>{group_name}</b> произошли изменения.\n\nПроверьте актуальное расписание на сайте pkeu.ru или используйте кнопки бота."
            
            for user_tuple in users:
                user_id = user_tuple[0]
                try:
                    await bot.send_message(user_id, message)
                    logging.info(f"Sent change notification to user {user_id} for group {group_name}")
                except Exception as e:
                    logging.error(f"Error sending change notification to user {user_id}: {e}")
    except Exception as e:
        logging.error(f"Error in change notification: {e}")

def setup_scheduler(db: Database, bot=None):
    scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")
    
    # Check for new schedule every 30 minutes
    if bot:
        scheduler.add_job(
            run_initial_parsing, 
            'interval', 
            minutes=30, 
            args=(db, bot), 
            name="Schedule Check"
        )
    else:
        scheduler.add_job(
            run_initial_parsing, 
            'interval', 
            minutes=30, 
            args=(db,), 
            name="Schedule Check"
        )
    
    # Morning notifications
    if bot:
        # Course 1 and 3 at 07:30
        scheduler.add_job(
            send_morning_notification, 
            'cron', 
            hour=7, 
            minute=30, 
            args=(db, bot, 1), 
            name="Morning Notification Course 1"
        )
        scheduler.add_job(
            send_morning_notification, 
            'cron', 
            hour=7, 
            minute=30, 
            args=(db, bot, 3), 
            name="Morning Notification Course 3"
        )
        
        # Course 2 at 10:00
        scheduler.add_job(
            send_morning_notification, 
            'cron', 
            hour=10, 
            minute=0, 
            args=(db, bot, 2), 
            name="Morning Notification Course 2"
        )
        
        # Evening notification at 20:00
        scheduler.add_job(
            send_evening_notification, 
            'cron', 
            hour=20, 
            minute=0, 
            args=(db, bot), 
            name="Evening Notification"
        )
    
    logging.info("Scheduler has been configured with notification jobs.")
    return scheduler