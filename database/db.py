import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL,
                education_base TEXT CHECK(education_base IN ('9', '11')),
                course INTEGER,
                group_name TEXT,
                notifications_pairs INTEGER DEFAULT 1,
                notifications_changes INTEGER DEFAULT 1,
                notifications_schedule INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                base TEXT CHECK(base IN ('9', '11')),
                course INTEGER,
                speciality TEXT
            )
        """)

        # Schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                parse_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                groups_data TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    # User operations
    def add_user(self, tg_id: int) -> bool:
        """Add new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (tg_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding user {tg_id}: {e}")
            return False

    def get_user(self, tg_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram ID"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user {tg_id}: {e}")
            return None

    def update_user_group(self, tg_id: int, education_base: str, course: int, group_name: str) -> bool:
        """Update user's group information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET education_base = ?, course = ?, group_name = ?
                WHERE tg_id = ?
            """, (education_base, course, group_name, tg_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating user {tg_id}: {e}")
            return False

    def update_user_notifications(self, tg_id: int, notif_type: str, value: int) -> bool:
        """Update user notification settings"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if notif_type == "pairs":
                cursor.execute("UPDATE users SET notifications_pairs = ? WHERE tg_id = ?", (value, tg_id))
            elif notif_type == "changes":
                cursor.execute("UPDATE users SET notifications_changes = ? WHERE tg_id = ?", (value, tg_id))
            elif notif_type == "schedule":
                cursor.execute("UPDATE users SET notifications_schedule = ? WHERE tg_id = ?", (value, tg_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating notifications for user {tg_id}: {e}")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def get_users_count(self) -> int:
        """Get total number of users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting users count: {e}")
            return 0

    # Group operations
    def add_group(self, name: str, base: str, course: int, speciality: str = "") -> bool:
        """Add new group"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO groups (name, base, course, speciality)
                VALUES (?, ?, ?, ?)
            """, (name, base, course, speciality))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding group {name}: {e}")
            return False

    def get_groups_by_base_and_course(self, base: str, course: int) -> List[str]:
        """Get groups by education base and course"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM groups 
                WHERE base = ? AND course = ?
                ORDER BY name
            """, (base, course))
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Error getting groups for base {base}, course {course}: {e}")
            return []

    # Schedule operations
    def add_schedule(self, file_path: str, groups_data: Dict[str, Any]) -> bool:
        """Add new schedule"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schedules (file_path, groups_data)
                VALUES (?, ?)
            """, (file_path, json.dumps(groups_data)))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding schedule {file_path}: {e}")
            return False

    def get_latest_schedule(self) -> Optional[Dict[str, Any]]:
        """Get latest schedule"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM schedules 
                ORDER BY parse_date DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            if row:
                result = dict(row)
                result['groups_data'] = json.loads(result['groups_data'])
                return result
            return None
        except Exception as e:
            logger.error(f"Error getting latest schedule: {e}")
            return None
