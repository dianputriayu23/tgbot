"""
Database module for storing user preferences and schedule data.
Auto-initializes SQLite database on first run.
"""

import aiosqlite
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import os

logger = logging.getLogger(__name__)


class Database:
    """Handles all database operations for the bot."""
    
    def __init__(self, db_path: str = "schedule.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
        
    async def connect(self):
        """Establish database connection."""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def close(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def initialize(self):
        """Create all necessary tables if they don't exist."""
        if not self.connection:
            await self.connect()
        
        try:
            # Users table
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    course INTEGER,
                    group_name TEXT,
                    notifications_enabled INTEGER DEFAULT 1,
                    notification_time TEXT DEFAULT '08:00',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Schedule cache table
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS schedule_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    sheet_name TEXT NOT NULL,
                    course INTEGER,
                    group_name TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    date TEXT,
                    time_slot TEXT NOT NULL,
                    subject TEXT,
                    room TEXT,
                    teacher TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_name, sheet_name, group_name, date, time_slot)
                )
            """)
            
            # Schedule files tracking
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS schedule_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    date_range TEXT,
                    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            await self.connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # User operations
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None) -> bool:
        """
        Add a new user or update existing user info.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            True if successful
        """
        try:
            await self.connection.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    updated_at=CURRENT_TIMESTAMP
            """, (user_id, username, first_name, last_name))
            await self.connection.commit()
            logger.info(f"User {user_id} added/updated")
            return True
        except Exception as e:
            logger.error(f"Failed to add user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data as dictionary or None
        """
        try:
            async with self.connection.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    async def update_user_group(self, user_id: int, course: int, group_name: str) -> bool:
        """
        Update user's course and group.
        
        Args:
            user_id: Telegram user ID
            course: Course number (1, 2, 3, etc.)
            group_name: Group name (e.g., "БУ1-24")
            
        Returns:
            True if successful
        """
        try:
            await self.connection.execute("""
                UPDATE users SET course = ?, group_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (course, group_name, user_id))
            await self.connection.commit()
            logger.info(f"Updated group for user {user_id}: {course} курс, {group_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update group for user {user_id}: {e}")
            return False
    
    async def update_notifications(self, user_id: int, enabled: bool, time: str = None) -> bool:
        """
        Update user's notification settings.
        
        Args:
            user_id: Telegram user ID
            enabled: Whether notifications are enabled
            time: Notification time in HH:MM format
            
        Returns:
            True if successful
        """
        try:
            if time:
                await self.connection.execute("""
                    UPDATE users 
                    SET notifications_enabled = ?, notification_time = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (int(enabled), time, user_id))
            else:
                await self.connection.execute("""
                    UPDATE users 
                    SET notifications_enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (int(enabled), user_id))
            await self.connection.commit()
            logger.info(f"Updated notifications for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update notifications for user {user_id}: {e}")
            return False
    
    # Schedule operations
    async def add_schedule_entry(self, file_name: str, sheet_name: str, 
                                 course: int, group_name: str,
                                 day_of_week: str, date: str, time_slot: str,
                                 subject: str = None, room: str = None, 
                                 teacher: str = None) -> bool:
        """
        Add or update a schedule entry.
        
        Args:
            file_name: Name of the schedule file
            sheet_name: Name of the Excel sheet
            course: Course number
            group_name: Group name
            day_of_week: Day of the week
            date: Date in YYYY-MM-DD format
            time_slot: Time slot (e.g., "III пара 12:30-13:50")
            subject: Subject name
            room: Room number
            teacher: Teacher name
            
        Returns:
            True if successful
        """
        try:
            await self.connection.execute("""
                INSERT INTO schedule_cache 
                (file_name, sheet_name, course, group_name, day_of_week, date, 
                 time_slot, subject, room, teacher)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_name, sheet_name, group_name, date, time_slot) 
                DO UPDATE SET
                    subject=excluded.subject,
                    room=excluded.room,
                    teacher=excluded.teacher,
                    created_at=CURRENT_TIMESTAMP
            """, (file_name, sheet_name, course, group_name, day_of_week, 
                  date, time_slot, subject, room, teacher))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add schedule entry: {e}")
            return False
    
    async def get_schedule_for_group(self, group_name: str, date: str = None) -> List[Dict[str, Any]]:
        """
        Get schedule for a specific group.
        
        Args:
            group_name: Group name
            date: Optional date filter in YYYY-MM-DD format
            
        Returns:
            List of schedule entries
        """
        try:
            if date:
                query = """
                    SELECT * FROM schedule_cache 
                    WHERE group_name = ? AND date = ?
                    ORDER BY date, time_slot
                """
                params = (group_name, date)
            else:
                query = """
                    SELECT * FROM schedule_cache 
                    WHERE group_name = ?
                    ORDER BY date, time_slot
                """
                params = (group_name,)
            
            async with self.connection.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get schedule for group {group_name}: {e}")
            return []
    
    async def add_schedule_file(self, file_name: str, file_path: str, 
                               date_range: str = None) -> bool:
        """
        Track a parsed schedule file.
        
        Args:
            file_name: Name of the file
            file_path: Path to the file
            date_range: Date range covered by the file
            
        Returns:
            True if successful
        """
        try:
            await self.connection.execute("""
                INSERT INTO schedule_files (file_name, file_path, date_range)
                VALUES (?, ?, ?)
                ON CONFLICT(file_name) DO UPDATE SET
                    file_path=excluded.file_path,
                    date_range=excluded.date_range,
                    parsed_at=CURRENT_TIMESTAMP
            """, (file_name, file_path, date_range))
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add schedule file {file_name}: {e}")
            return False
    
    async def get_users_for_notifications(self) -> List[Dict[str, Any]]:
        """
        Get all users who have notifications enabled.
        
        Returns:
            List of users with notification settings
        """
        try:
            async with self.connection.execute("""
                SELECT * FROM users 
                WHERE notifications_enabled = 1 AND group_name IS NOT NULL
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get users for notifications: {e}")
            return []
