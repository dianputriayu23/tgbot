import logging
from datetime import datetime, time
from typing import Optional
from database.db import Database
from aiogram import Bot

class NotificationService:
    """Service for managing user notifications"""
    
    def __init__(self, db: Database, bot: Bot):
        self.db = db
        self.bot = bot
    
    async def send_morning_reminder(self, user_id: int, group_name: str, notify_time: Optional[time] = None):
        """
        Send morning reminder to user about today's schedule
        
        Args:
            user_id: Telegram user ID
            group_name: User's group name
            notify_time: Time when notification should be sent (default: 07:30)
        """
        try:
            today = datetime.now()
            weekday_index = today.weekday()
            
            # Skip Sunday (weekday 6)
            if weekday_index == 6:
                return
            
            days_ru = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
            day_name = days_ru[weekday_index]
            
            # Get schedule for today
            lessons = await self.db.get_schedule_for_group(group_name, day_name)
            
            if not lessons:
                message = f"📅 Доброе утро! ☀️\n\nНа сегодня ({day_name}) пар нет! 🎉"
            else:
                message = f"📅 Доброе утро! ☀️\n\n<b>Расписание на сегодня ({day_name})</b>\n\n"
                
                for lesson in lessons:
                    lesson_num = lesson[4]
                    time_start = lesson[5]
                    time_end = lesson[6]
                    subject = lesson[7]
                    teacher = lesson[8]
                    cabinet = lesson[9]
                    
                    message += f"<b>{lesson_num} пара ({time_start} - {time_end})</b>\n"
                    message += f"🔹 <b>{subject}</b>\n"
                    if teacher:
                        message += f"👤 {teacher}\n"
                    if cabinet:
                        message += f"🚪 {cabinet}\n"
                    message += "\n"
            
            await self.bot.send_message(user_id, message)
            logging.info(f"Morning reminder sent to user {user_id}")
            
        except Exception as e:
            logging.error(f"Error sending morning reminder to user {user_id}: {e}", exc_info=True)
    
    async def send_schedule_change_notification(self, user_id: int, message: str):
        """
        Send notification about schedule changes
        
        Args:
            user_id: Telegram user ID
            message: Notification message
        """
        try:
            notification = f"🔔 <b>Внимание! Изменение в расписании</b>\n\n{message}"
            await self.bot.send_message(user_id, notification)
            logging.info(f"Schedule change notification sent to user {user_id}")
        except Exception as e:
            logging.error(f"Error sending schedule change notification to user {user_id}: {e}", exc_info=True)
    
    async def send_lesson_reminder(self, user_id: int, lesson_info: dict, minutes_before: int = 30):
        """
        Send reminder before a lesson starts
        
        Args:
            user_id: Telegram user ID
            lesson_info: Dictionary with lesson details
            minutes_before: How many minutes before lesson to send reminder
        """
        try:
            message = (
                f"⏰ <b>Напоминание о паре</b>\n\n"
                f"Через {minutes_before} минут начинается:\n"
                f"<b>{lesson_info.get('subject', 'N/A')}</b>\n"
                f"🕐 {lesson_info.get('time_start', 'N/A')} - {lesson_info.get('time_end', 'N/A')}\n"
            )
            
            if lesson_info.get('teacher'):
                message += f"👤 {lesson_info['teacher']}\n"
            if lesson_info.get('cabinet'):
                message += f"🚪 {lesson_info['cabinet']}\n"
            
            await self.bot.send_message(user_id, message)
            logging.info(f"Lesson reminder sent to user {user_id}")
        except Exception as e:
            logging.error(f"Error sending lesson reminder to user {user_id}: {e}", exc_info=True)
    
    async def notify_all_users_about_changes(self, affected_groups: list):
        """
        Notify all users from affected groups about schedule changes
        
        Args:
            affected_groups: List of group names that were affected by changes
        """
        try:
            # Get all users who have notifications enabled
            users = await self.db.execute(
                "SELECT user_id, group_name FROM users WHERE notify_changes = TRUE AND group_name IS NOT NULL",
                fetch='all'
            )
            
            if not users:
                logging.info("No users to notify about changes")
                return
            
            notified_count = 0
            for user_id, group_name in users:
                if group_name in affected_groups:
                    message = (
                        f"Расписание для вашей группы <b>{group_name}</b> обновлено!\n"
                        f"Проверьте новое расписание в боте."
                    )
                    await self.send_schedule_change_notification(user_id, message)
                    notified_count += 1
            
            logging.info(f"Notified {notified_count} users about schedule changes")
            
        except Exception as e:
            logging.error(f"Error notifying users about changes: {e}", exc_info=True)
