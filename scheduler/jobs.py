import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from database.db import Database
from parser.parser import ScheduleParser

logger = logging.getLogger(__name__)


class SchedulerJobs:
    def __init__(self, bot, db: Database, parser: ScheduleParser):
        self.bot = bot
        self.db = db
        self.parser = parser
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start all scheduled jobs"""
        # Check for new schedule every 20 minutes
        self.scheduler.add_job(
            self.check_schedule,
            trigger=IntervalTrigger(minutes=20),
            id="check_schedule",
            name="Check for new schedule",
            replace_existing=True
        )

        # Morning notifications for 1st and 3rd year - 7:30
        self.scheduler.add_job(
            self.send_morning_notifications_1_3,
            trigger=CronTrigger(hour=7, minute=30),
            id="morning_notif_1_3",
            name="Morning notifications for 1st and 3rd year",
            replace_existing=True
        )

        # Morning notifications for 2nd year - 10:00
        self.scheduler.add_job(
            self.send_morning_notifications_2,
            trigger=CronTrigger(hour=10, minute=0),
            id="morning_notif_2",
            name="Morning notifications for 2nd year",
            replace_existing=True
        )

        # Evening notifications about new schedule - 18:00
        self.scheduler.add_job(
            self.send_evening_notifications,
            trigger=CronTrigger(hour=18, minute=0),
            id="evening_notif",
            name="Evening notifications about new schedule",
            replace_existing=True
        )

        # Clean up old files - daily at 3:00 AM
        self.scheduler.add_job(
            self.cleanup_old_files,
            trigger=CronTrigger(hour=3, minute=0),
            id="cleanup_files",
            name="Clean up old schedule files",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Scheduler started with all jobs")

    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def check_schedule(self):
        """Check for new schedule files"""
        try:
            logger.info("Checking for new schedule...")
            # TODO: Implement schedule checking logic
            # - Check website for new files
            # - Download if new
            # - Parse and save to DB
            # - Notify users about changes
        except Exception as e:
            logger.error(f"Error checking schedule: {e}")

    async def send_morning_notifications_1_3(self):
        """Send morning notifications to 1st and 3rd year students"""
        try:
            logger.info("Sending morning notifications for 1st and 3rd year...")
            users = self.db.get_all_users()
            
            for user in users:
                if user.get('notifications_pairs') and user.get('course') in [1, 3]:
                    try:
                        # Get today's schedule for this user
                        # For now, just send a reminder
                        await self.bot.send_message(
                            user['tg_id'],
                            f"🔔 Доброе утро!\n\n"
                            f"Сегодня {datetime.now().strftime('%d.%m.%Y')}\n"
                            f"Проверьте расписание с помощью кнопки 'Сегодня'"
                        )
                    except Exception as e:
                        logger.error(f"Error sending notification to user {user['tg_id']}: {e}")
        except Exception as e:
            logger.error(f"Error in morning notifications 1,3: {e}")

    async def send_morning_notifications_2(self):
        """Send morning notifications to 2nd year students"""
        try:
            logger.info("Sending morning notifications for 2nd year...")
            users = self.db.get_all_users()
            
            for user in users:
                if user.get('notifications_pairs') and user.get('course') == 2:
                    try:
                        await self.bot.send_message(
                            user['tg_id'],
                            f"🔔 Доброе утро!\n\n"
                            f"Сегодня {datetime.now().strftime('%d.%m.%Y')}\n"
                            f"Проверьте расписание с помощью кнопки 'Сегодня'"
                        )
                    except Exception as e:
                        logger.error(f"Error sending notification to user {user['tg_id']}: {e}")
        except Exception as e:
            logger.error(f"Error in morning notifications 2: {e}")

    async def send_evening_notifications(self):
        """Send evening notifications about new schedule"""
        try:
            logger.info("Sending evening notifications about new schedule...")
            users = self.db.get_all_users()
            
            # TODO: Check if there's actually a new schedule
            has_new_schedule = False  # Implement actual check
            
            if has_new_schedule:
                for user in users:
                    if user.get('notifications_schedule'):
                        try:
                            await self.bot.send_message(
                                user['tg_id'],
                                "🔔 Добавлено новое расписание!\n\n"
                                "Проверьте актуальное расписание."
                            )
                        except Exception as e:
                            logger.error(f"Error sending notification to user {user['tg_id']}: {e}")
        except Exception as e:
            logger.error(f"Error in evening notifications: {e}")

    async def cleanup_old_files(self):
        """Clean up old schedule files"""
        try:
            logger.info("Cleaning up old files...")
            self.parser.cleanup_old_files(days=8)
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
