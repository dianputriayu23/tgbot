"""
Scheduler module for periodic tasks.
Handles notifications and schedule updates.
"""

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

if TYPE_CHECKING:
    from telegram import Bot
    from database import Database
    from parser import ScheduleParser

logger = logging.getLogger(__name__)


class ScheduleJobManager:
    """Manages scheduled jobs for the bot."""
    
    def __init__(self, bot, db, parser, schedule_folder: str = "."):
        """
        Initialize job manager.
        
        Args:
            bot: Telegram bot instance
            db: Database instance
            parser: Schedule parser instance
            schedule_folder: Folder containing schedule files
        """
        self.bot = bot
        self.db = db
        self.parser = parser
        self.schedule_folder = schedule_folder
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Start the scheduler."""
        # Add jobs
        self.add_notification_jobs()
        self.add_schedule_update_job()
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    def add_notification_jobs(self):
        """Add notification jobs for different times."""
        # Add job for each hour from 6 AM to 11 AM
        for hour in range(6, 12):
            trigger = CronTrigger(hour=hour, minute=0)
            self.scheduler.add_job(
                self.send_scheduled_notifications,
                trigger=trigger,
                id=f'notifications_{hour:02d}:00',
                name=f'Send notifications at {hour:02d}:00'
            )
            logger.info(f"Added notification job for {hour:02d}:00")
    
    def add_schedule_update_job(self):
        """Add job to check for schedule updates."""
        # Check for new schedule files every hour
        trigger = CronTrigger(minute=0)
        self.scheduler.add_job(
            self.update_schedule_cache,
            trigger=trigger,
            id='schedule_update',
            name='Update schedule cache'
        )
        logger.info("Added schedule update job")
    
    async def send_scheduled_notifications(self):
        """Send schedule notifications to users at their preferred time."""
        try:
            current_time = datetime.now().strftime('%H:%M')
            logger.info(f"Checking for users to notify at {current_time}")
            
            # Get users who want notifications at this time
            users = await self.db.get_users_for_notifications()
            
            notified_count = 0
            for user in users:
                user_time = user.get('notification_time', '08:00')
                
                # Check if this is the right time for this user (allow 1 minute tolerance)
                if user_time == current_time or user_time == datetime.now().strftime('%H:%M'):
                    await self.send_daily_schedule(user)
                    notified_count += 1
            
            if notified_count > 0:
                logger.info(f"Sent notifications to {notified_count} users")
        
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    async def send_daily_schedule(self, user: dict):
        """
        Send daily schedule to a user.
        
        Args:
            user: User data dictionary
        """
        try:
            user_id = user['user_id']
            group_name = user.get('group_name')
            
            if not group_name:
                return
            
            # Get today's schedule
            today = datetime.now().date()
            date_str = today.strftime('%Y-%m-%d')
            
            schedule = await self.db.get_schedule_for_group(group_name, date_str)
            
            if not schedule:
                # No schedule for today
                message = (
                    f"📅 Доброе утро!\n\n"
                    f"Расписание на сегодня ({today.strftime('%d.%m.%Y')}):\n"
                    f"Группа: {group_name}\n\n"
                    f"📝 Занятий нет или расписание не загружено"
                )
            else:
                # Format schedule
                day_name = schedule[0]['day_of_week'].title()
                message = (
                    f"📅 Доброе утро!\n\n"
                    f"Расписание на сегодня:\n"
                    f"{day_name}, {today.strftime('%d.%m.%Y')}\n"
                    f"Группа: {group_name}\n\n"
                )
                
                for entry in schedule:
                    message += f"⏰ {entry['time_slot']}\n"
                    message += f"📚 {entry['subject']}\n"
                    
                    if entry['teacher']:
                        message += f"👨‍🏫 {entry['teacher']}\n"
                    
                    if entry['room']:
                        message += f"🏫 Аудитория: {entry['room']}\n"
                    
                    message += "\n"
                
                message += "Хорошего дня! 😊"
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message
            )
            
            logger.info(f"Sent daily schedule to user {user_id}")
        
        except Exception as e:
            logger.error(f"Error sending daily schedule to user {user.get('user_id')}: {e}")
    
    async def update_schedule_cache(self):
        """Update schedule cache from Excel files."""
        try:
            logger.info("Checking for schedule updates...")
            
            # Find all schedule files
            files = self.parser.find_schedule_files(self.schedule_folder)
            
            if not files:
                logger.info("No schedule files found")
                return
            
            updated_count = 0
            
            for file_path in files:
                try:
                    # Parse the file
                    entries = self.parser.parse_file(file_path)
                    
                    if not entries:
                        logger.warning(f"No entries found in {file_path}")
                        continue
                    
                    # Add to database
                    for entry in entries:
                        await self.db.add_schedule_entry(
                            file_name=entry['file_name'],
                            sheet_name=entry['sheet_name'],
                            course=entry['course'],
                            group_name=entry['group_name'],
                            day_of_week=entry['day_of_week'],
                            date=entry['date'],
                            time_slot=entry['time_slot'],
                            subject=entry['subject'],
                            room=entry['room'],
                            teacher=entry['teacher']
                        )
                    
                    # Track the file
                    await self.db.add_schedule_file(
                        file_name=entry['file_name'],
                        file_path=file_path
                    )
                    
                    updated_count += 1
                    logger.info(f"Updated schedule from {file_path}: {len(entries)} entries")
                
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
            
            if updated_count > 0:
                logger.info(f"Schedule cache updated from {updated_count} files")
        
        except Exception as e:
            logger.error(f"Error updating schedule cache: {e}")
    
    async def manual_schedule_update(self):
        """Manually trigger schedule update (can be called from admin command)."""
        logger.info("Manual schedule update triggered")
        await self.update_schedule_cache()
