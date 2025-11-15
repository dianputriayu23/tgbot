"""
Database module for Telegram bot
Handles all database operations with SQLite
"""
import aiosqlite
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Database manager for the bot"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize database and create tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    base INTEGER,
                    course INTEGER,
                    group_name TEXT,
                    notifications_enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Groups table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    base INTEGER NOT NULL,
                    course INTEGER NOT NULL,
                    group_name TEXT NOT NULL,
                    UNIQUE(base, course, group_name)
                )
            """)
            
            # Schedules table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    base INTEGER NOT NULL,
                    course INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    lesson_number INTEGER NOT NULL,
                    subject TEXT,
                    teacher TEXT,
                    room TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None):
        """Add new user or update existing user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, username, first_name, last_name))
            await db.commit()
    
    async def update_user_group(self, user_id: int, base: int, course: int, group_name: str):
        """Update user's group selection"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET base = ?, course = ?, group_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (base, course, group_name, user_id))
            await db.commit()
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def set_notifications(self, user_id: int, enabled: bool):
        """Enable or disable notifications for user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users 
                SET notifications_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (1 if enabled else 0, user_id))
            await db.commit()
    
    async def add_group(self, base: int, course: int, group_name: str):
        """Add a new group"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO groups (base, course, group_name)
                    VALUES (?, ?, ?)
                """, (base, course, group_name))
                await db.commit()
            except aiosqlite.IntegrityError:
                # Group already exists
                pass
    
    async def get_groups(self, base: int, course: int) -> List[str]:
        """Get all groups for a specific base and course"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT DISTINCT group_name FROM groups
                WHERE base = ? AND course = ?
                ORDER BY group_name
            """, (base, course)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def add_schedule(self, group_name: str, base: int, course: int, 
                          date: str, day_of_week: str, lesson_number: int,
                          subject: str = None, teacher: str = None, room: str = None):
        """Add schedule entry"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO schedules 
                (group_name, base, course, date, day_of_week, lesson_number, subject, teacher, room)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (group_name, base, course, date, day_of_week, lesson_number, subject, teacher, room))
            await db.commit()
    
    async def get_schedule(self, group_name: str, date: str) -> List[Dict[str, Any]]:
        """Get schedule for a specific group and date"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM schedules
                WHERE group_name = ? AND date = ?
                ORDER BY lesson_number
            """, (group_name, date)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_week_schedule(self, group_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get schedule for a week"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM schedules
                WHERE group_name = ? AND date BETWEEN ? AND ?
                ORDER BY date, lesson_number
            """, (group_name, start_date, end_date)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def clear_schedule(self):
        """Clear all schedule data"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM schedules")
            await db.commit()
    
    async def get_users_with_notifications(self) -> List[Dict[str, Any]]:
        """Get all users with notifications enabled"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM users 
                WHERE notifications_enabled = 1 AND group_name IS NOT NULL
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
