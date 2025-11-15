"""
Scheduler jobs for automatic tasks and notifications
"""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from database import Database
from parser import parse_schedule_file

logger = logging.getLogger(__name__)


class SchedulerJobs:
    """Manages scheduled jobs for the bot"""
    
    def __init__(self, bot: Bot, db: Database, schedule_dir: str):
        self.bot = bot
        self.db = db
        self.schedule_dir = schedule_dir
        self.scheduler = AsyncIOScheduler()
    
    async def send_daily_notifications(self):
        """Send daily schedule notifications to users"""
        try:
            logger.info("Starting daily notifications")
            
            # Get tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            tomorrow_formatted = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')
            
            # Get all users with notifications enabled
            users = await self.db.get_users_with_notifications()
            
            logger.info(f"Found {len(users)} users with notifications enabled")
            
            for user in users:
                try:
                    group_name = user.get('group_name')
                    if not group_name:
                        continue
                    
                    # Get schedule for tomorrow
                    schedule = await self.db.get_schedule(group_name, tomorrow)
                    
                    if not schedule:
                        # No schedule for tomorrow
                        message = (
                            f"📅 Расписание на завтра ({tomorrow_formatted})\n"
                            f"Группа: {group_name}\n\n"
                            f"📭 На завтра нет занятий или расписание еще не загружено."
                        )
                    else:
                        # Format schedule
                        message = f"📅 Расписание на завтра ({tomorrow_formatted})\n"
                        message += f"Группа: {group_name}\n"
                        
                        if schedule[0].get('day_of_week'):
                            message += f"День: {schedule[0]['day_of_week']}\n"
                        
                        message += "\n"
                        
                        for lesson in schedule:
                            message += f"▫️ Пара {lesson['lesson_number']}\n"
                            
                            if lesson.get('subject'):
                                message += f"  📚 {lesson['subject']}\n"
                            
                            if lesson.get('teacher'):
                                message += f"  👨‍🏫 {lesson['teacher']}\n"
                            
                            if lesson.get('room'):
                                message += f"  🚪 Кабинет: {lesson['room']}\n"
                            
                            message += "\n"
                    
                    # Send notification
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=message
                    )
                    
                    logger.info(f"Sent notification to user {user['user_id']}")
                    
                except Exception as e:
                    logger.error(f"Error sending notification to user {user.get('user_id')}: {e}")
            
            logger.info("Daily notifications completed")
            
        except Exception as e:
            logger.error(f"Error in daily notifications job: {e}")
    
    async def update_schedules(self):
        """Update schedules from XLSX files in the directory"""
        try:
            logger.info("Starting schedule update")
            
            # Find all XLSX files in the directory
            xlsx_files = list(Path(self.schedule_dir).glob("*.xlsx"))
            
            if not xlsx_files:
                logger.warning("No XLSX files found for schedule update")
                return
            
            logger.info(f"Found {len(xlsx_files)} XLSX files")
            
            # Clear old schedules
            await self.db.clear_schedule()
            
            # Parse each file
            total_entries = 0
            for xlsx_file in xlsx_files:
                try:
                    logger.info(f"Parsing file: {xlsx_file.name}")
                    
                    schedule_data = await parse_schedule_file(str(xlsx_file))
                    
                    logger.info(f"Found {len(schedule_data)} schedule entries in {xlsx_file.name}")
                    
                    # Add to database
                    for entry in schedule_data:
                        await self.db.add_schedule(
                            group_name=entry['group_name'],
                            base=entry['base'],
                            course=entry['course'],
                            date=entry['date'],
                            day_of_week=entry['day_of_week'],
                            lesson_number=entry['lesson_number'],
                            subject=entry.get('subject'),
                            teacher=entry.get('teacher'),
                            room=entry.get('room')
                        )
                        
                        # Also register the group
                        await self.db.add_group(
                            base=entry['base'],
                            course=entry['course'],
                            group_name=entry['group_name']
                        )
                    
                    total_entries += len(schedule_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing file {xlsx_file.name}: {e}")
            
            logger.info(f"Schedule update completed. Total entries: {total_entries}")
            
        except Exception as e:
            logger.error(f"Error in schedule update job: {e}")
    
    def start(self):
        """Start the scheduler"""
        # Update schedules on startup
        self.scheduler.add_job(
            self.update_schedules,
            'date',
            run_date=datetime.now() + timedelta(seconds=10)
        )
        
        # Update schedules daily at 3 AM
        self.scheduler.add_job(
            self.update_schedules,
            'cron',
            hour=3,
            minute=0
        )
        
        # Send daily notifications at 6 PM
        notification_time = os.getenv('NOTIFICATION_TIME', '18:00').split(':')
        self.scheduler.add_job(
            self.send_daily_notifications,
            'cron',
            hour=int(notification_time[0]),
            minute=int(notification_time[1])
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
