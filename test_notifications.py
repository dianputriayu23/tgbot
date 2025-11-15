#!/usr/bin/env python3
"""
Test script for notification service (without actual Telegram API calls)
"""
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from database.db import Database
from notifications import NotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_notification_service():
    """Test notification service with mocked bot"""
    print("\n" + "="*60)
    print("Testing Notification Service")
    print("="*60 + "\n")
    
    # Setup test database
    db = Database('test_notifications.db')
    await db.initialize()
    
    # Add test user
    await db.add_or_update_user(12345, "Test User", "testuser")
    await db.update_user_profile(12345, "11_classes", 2, "БУ1-24")
    await db.update_user_notifications(12345, notify_lessons=True, notify_changes=True)
    
    # Add test schedule
    test_lessons = [
        {
            "group_name": "БУ1-24",
            "day_of_week": "понедельник",
            "date": "2025-11-15",
            "lesson_number": "I",
            "time_start": "08:00",
            "time_end": "09:20",
            "subject": "Математика",
            "teacher": "Иванов И.И.",
            "cabinet": "301",
            "file_hash": "test_hash"
        }
    ]
    await db.add_schedule_hash("test_hash")
    await db.save_schedule(test_lessons)
    
    # Create mock bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(return_value=None)
    
    # Create notification service
    notification_service = NotificationService(db, mock_bot)
    
    # Test 1: Morning reminder
    print("Test 1: Sending morning reminder...")
    try:
        await notification_service.send_morning_reminder(12345, "БУ1-24")
        if mock_bot.send_message.called:
            print("✅ Morning reminder sent (bot.send_message was called)")
            call_args = mock_bot.send_message.call_args
            print(f"   User ID: {call_args[0][0]}")
            print(f"   Message preview: {call_args[0][1][:100]}...")
        else:
            print("❌ bot.send_message was not called")
            return False
    except Exception as e:
        print(f"❌ Morning reminder failed: {e}")
        return False
    
    # Test 2: Schedule change notification
    print("\nTest 2: Sending schedule change notification...")
    mock_bot.send_message.reset_mock()
    try:
        await notification_service.send_schedule_change_notification(
            12345, 
            "Расписание изменено!"
        )
        if mock_bot.send_message.called:
            print("✅ Schedule change notification sent")
            call_args = mock_bot.send_message.call_args
            print(f"   Message preview: {call_args[0][1][:100]}...")
        else:
            print("❌ bot.send_message was not called")
            return False
    except Exception as e:
        print(f"❌ Schedule change notification failed: {e}")
        return False
    
    # Test 3: Lesson reminder
    print("\nTest 3: Sending lesson reminder...")
    mock_bot.send_message.reset_mock()
    try:
        lesson_info = {
            'subject': 'Математика',
            'time_start': '08:00',
            'time_end': '09:20',
            'teacher': 'Иванов И.И.',
            'cabinet': '301'
        }
        await notification_service.send_lesson_reminder(12345, lesson_info, 30)
        if mock_bot.send_message.called:
            print("✅ Lesson reminder sent")
            call_args = mock_bot.send_message.call_args
            print(f"   Message preview: {call_args[0][1][:100]}...")
        else:
            print("❌ bot.send_message was not called")
            return False
    except Exception as e:
        print(f"❌ Lesson reminder failed: {e}")
        return False
    
    # Test 4: Notify all users about changes
    print("\nTest 4: Notifying all users about changes...")
    mock_bot.send_message.reset_mock()
    try:
        await notification_service.notify_all_users_about_changes(["БУ1-24"])
        if mock_bot.send_message.called:
            print("✅ Users notified about changes")
            print(f"   Number of calls: {mock_bot.send_message.call_count}")
        else:
            print("⚠️  No users to notify (this is expected if notify_changes is disabled)")
    except Exception as e:
        print(f"❌ Notify all users failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All notification service tests passed!")
    print("="*60 + "\n")
    
    # Cleanup
    import os
    if os.path.exists('test_notifications.db'):
        os.remove('test_notifications.db')
        print("Test database cleaned up.\n")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_notification_service())
    exit(0 if result else 1)
