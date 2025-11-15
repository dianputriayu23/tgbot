#!/usr/bin/env python3
"""
Test script for validating bot functionality
"""
import asyncio
import logging
import sys
from database.db import Database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_database():
    """Test database initialization and basic operations"""
    print("\n" + "="*60)
    print("Testing Database Module")
    print("="*60 + "\n")
    
    db = Database('test_schedule.db')
    
    # Test 1: Initialize database
    print("Test 1: Initializing database...")
    try:
        await db.initialize()
        print("✅ Database initialized successfully\n")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}\n")
        return False
    
    # Test 2: Add user
    print("Test 2: Adding test user...")
    try:
        await db.add_or_update_user(12345, "Test User", "testuser")
        user = await db.get_user(12345)
        if user:
            print(f"✅ User added successfully: {user}\n")
        else:
            print("❌ Failed to retrieve user\n")
            return False
    except Exception as e:
        print(f"❌ User addition failed: {e}\n")
        return False
    
    # Test 3: Update user profile
    print("Test 3: Updating user profile...")
    try:
        await db.update_user_profile(12345, "11_classes", 2, "БУ1-24")
        user = await db.get_user(12345)
        if user and user[5] == "БУ1-24":
            print(f"✅ User profile updated successfully: Group={user[5]}, Course={user[4]}\n")
        else:
            print("❌ Failed to update user profile\n")
            return False
    except Exception as e:
        print(f"❌ Profile update failed: {e}\n")
        return False
    
    # Test 4: Notification settings
    print("Test 4: Testing notification settings...")
    try:
        await db.update_user_notifications(12345, notify_lessons=False, notify_changes=True)
        user = await db.get_user(12345)
        if user and user[6] == 0 and user[7] == 1:
            print(f"✅ Notification settings updated successfully\n")
        else:
            print("❌ Failed to update notification settings\n")
            return False
    except Exception as e:
        print(f"❌ Notification update failed: {e}\n")
        return False
    
    # Test 5: Add test schedule data
    print("Test 5: Adding test schedule data...")
    try:
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
                "file_hash": "test_hash_123"
            },
            {
                "group_name": "БУ1-24",
                "day_of_week": "понедельник",
                "date": "2025-11-15",
                "lesson_number": "II",
                "time_start": "09:30",
                "time_end": "10:50",
                "subject": "Информатика",
                "teacher": "Петров П.П.",
                "cabinet": "302",
                "file_hash": "test_hash_123"
            }
        ]
        
        await db.add_schedule_hash("test_hash_123")
        await db.save_schedule(test_lessons)
        
        # Retrieve schedule
        schedule = await db.get_schedule_for_group("БУ1-24", "понедельник")
        if schedule and len(schedule) == 2:
            print(f"✅ Schedule data added successfully: {len(schedule)} lessons\n")
        else:
            print(f"❌ Failed to add schedule data\n")
            return False
    except Exception as e:
        print(f"❌ Schedule addition failed: {e}\n")
        return False
    
    # Test 6: Get all groups
    print("Test 6: Getting all groups...")
    try:
        groups = await db.get_all_groups()
        if groups and "БУ1-24" in groups:
            print(f"✅ Groups retrieved successfully: {groups}\n")
        else:
            print("❌ Failed to retrieve groups\n")
            return False
    except Exception as e:
        print(f"❌ Groups retrieval failed: {e}\n")
        return False
    
    # Test 7: Get users for morning reminder
    print("Test 7: Getting users for morning reminder...")
    try:
        # First enable notifications for test user
        await db.update_user_notifications(12345, notify_lessons=True)
        users = await db.get_users_for_morning_reminder()
        print(f"✅ Users for morning reminder: {len(users) if users else 0} users\n")
    except Exception as e:
        print(f"❌ Morning reminder query failed: {e}\n")
        return False
    
    print("="*60)
    print("✅ All database tests passed!")
    print("="*60 + "\n")
    
    # Cleanup
    import os
    if os.path.exists('test_schedule.db'):
        os.remove('test_schedule.db')
        print("Test database cleaned up.\n")
    
    return True

async def test_parser_imports():
    """Test that parser modules can be imported"""
    print("\n" + "="*60)
    print("Testing Parser Module Imports")
    print("="*60 + "\n")
    
    try:
        from parser.parser import clean_value, is_header_row
        print("✅ Parser utility functions imported successfully")
        
        # Test clean_value
        assert clean_value(None) == ""
        assert clean_value("  test  ") == "test"
        print("✅ clean_value function works correctly")
        
        # Test is_header_row
        test_row = ["", "", "", "", "", "БУ1-24", "ауд.", "Ф1-24"]
        assert is_header_row(test_row) == True
        print("✅ is_header_row function works correctly")
        
        print("\n" + "="*60)
        print("✅ All parser tests passed!")
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"❌ Parser tests failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "🧪 Starting Bot Component Tests" + "\n")
    
    results = []
    
    # Run database tests
    results.append(await test_database())
    
    # Run parser tests
    results.append(await test_parser_imports())
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED! 🎉")
        print("="*60 + "\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
