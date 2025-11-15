import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import Database
from parser.parser import run_initial_parsing

async def send_daily_schedule_notifications(db: Database, bot, course_filter=None):
    """Send daily schedule notifications to users"""
    from handlers.schedule_viewer import format_schedule, DAYS_RU
    
    logging.info(f"Starting daily schedule notifications (course filter: {course_filter})...")
    today = datetime.now()
    weekday = today.weekday()
    
    if weekday == 6:  # Skip Sunday
        return
    
    day_name = DAYS_RU[weekday]
    users = await db.get_users_with_notifications('lessons')
    
    for user_id, group_name, course in users:
        if not group_name:
            continue
        
        # Filter by course if specified
        if course_filter and course != course_filter:
            continue
            
        try:
            lessons = await db.get_schedule_for_group(group_name, day_name)
            if lessons:
                message = await format_schedule(lessons)
                message = f"🔔 <b>Напоминание о парах на сегодня</b>\n\n" + message
                await bot.send_message(user_id, message)
        except Exception as e:
            logging.error(f"Error sending notification to user {user_id}: {e}")

async def send_tomorrow_schedule_notifications(db: Database, bot):
    """Send tomorrow's schedule notifications"""
    from handlers.schedule_viewer import format_schedule, DAYS_RU
    
    logging.info("Starting tomorrow's schedule notifications...")
    tomorrow = datetime.now() + timedelta(days=1)
    weekday = tomorrow.weekday()
    
    if weekday == 6:  # Skip Sunday
        return
    
    day_name = DAYS_RU[weekday]
    users = await db.get_users_with_notifications('new_schedule')
    
    for user_id, group_name, _ in users if len(users[0]) > 2 else [(u[0], await db.get_user(u[0])[5], None) for u in users]:
        if not group_name:
            continue
            
        try:
            lessons = await db.get_schedule_for_group(group_name, day_name)
            if lessons:
                message = await format_schedule(lessons)
                message = f"📅 <b>Расписание на завтра</b>\n\n" + message
                await bot.send_message(user_id, message)
        except Exception as e:
            logging.error(f"Error sending tomorrow notification to user {user_id}: {e}")

async def cleanup_old_schedules(db: Database):
    """Clean up schedule files older than 8 days"""
    logging.info("Running schedule file cleanup...")
    await db.cleanup_old_files(days=8)

def setup_scheduler(db: Database, bot=None):
    scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")
    
    # Check for new schedules every 20 minutes
    scheduler.add_job(run_initial_parsing, 'interval', minutes=20, args=(db,), name="Schedule Check")
    
    # Daily notifications at 7:30 for 1st and 3rd year students
    if bot:
        scheduler.add_job(
            send_daily_schedule_notifications, 
            'cron', 
            hour=7, 
            minute=30, 
            args=(db, bot, 1),
            name="Morning Notifications (1st year)"
        )
        
        scheduler.add_job(
            send_daily_schedule_notifications, 
            'cron', 
            hour=7, 
            minute=30, 
            args=(db, bot, 3),
            name="Morning Notifications (3rd year)"
        )
        
        # Daily notifications at 10:00 for 2nd year students  
        scheduler.add_job(
            send_daily_schedule_notifications,
            'cron',
            hour=10,
            minute=0,
            args=(db, bot, 2),
            name="Morning Notifications (2nd year)"
        )
        
        # Evening notifications for tomorrow's schedule at 20:00
        scheduler.add_job(
            send_tomorrow_schedule_notifications,
            'cron',
            hour=20,
            minute=0,
            args=(db, bot),
            name="Evening Notifications"
        )
    
    # Cleanup old files daily at 3:00 AM
    scheduler.add_job(
        cleanup_old_schedules,
        'cron',
        hour=3,
        minute=0,
        args=(db,),
        name="File Cleanup"
    )
    
    logging.info("Scheduler has been configured.")
    return scheduler