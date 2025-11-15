import aiosqlite
import logging

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    async def execute(self, query, params=(), fetch=None):
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.cursor()
                await cursor.execute(query, params)
                await db.commit()
                if fetch == 'one': return await cursor.fetchone()
                if fetch == 'all': return await cursor.fetchall()
        except Exception as e:
            logging.error(f"Ошибка при работе с базой данных: {e}", exc_info=True)
            return None

    async def initialize(self):
        # ... (здесь ваш код initialize, он правильный)
        await self.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            education_form TEXT,
            course INTEGER,
            group_name TEXT,
            notify_lessons BOOLEAN DEFAULT TRUE,
            notify_changes BOOLEAN DEFAULT TRUE,
            morning_reminder_time TEXT DEFAULT '07:30',
            lesson_reminder_minutes INTEGER DEFAULT 30
        )
        """)
        await self.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            day_of_week TEXT,
            date TEXT,
            lesson_number TEXT,
            time_start TEXT,
            time_end TEXT,
            subject TEXT,
            teacher TEXT,
            cabinet TEXT,
            file_hash TEXT
        )
        """)
        await self.execute("""
        CREATE TABLE IF NOT EXISTS schedule_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_hash TEXT UNIQUE
        )
        """)
        
        # Create indexes for better query performance
        await self.execute("""
        CREATE INDEX IF NOT EXISTS idx_schedule_group_day 
        ON schedule(group_name, day_of_week)
        """)
        
        await self.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_group 
        ON users(group_name)
        """)
        
        await self.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_notifications 
        ON users(notify_lessons, notify_changes)
        """)
        
        logging.info("Таблицы в базе данных проверены/созданы.")
    
    async def add_or_update_user(self, user_id, full_name, username):
        # ... (ваш код)
        user = await self.get_user(user_id)
        if user:
            await self.execute("UPDATE users SET full_name = ?, username = ? WHERE user_id = ?", (full_name, username, user_id))
        else:
            await self.execute("INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)", (user_id, full_name, username))
    
    async def get_user(self, user_id):
        return await self.execute("SELECT * FROM users WHERE user_id = ?", (user_id,), fetch='one')

    async def update_user_profile(self, user_id, education_form, course, group_name):
        await self.execute("UPDATE users SET education_form = ?, course = ?, group_name = ? WHERE user_id = ?", (education_form, course, group_name, user_id))

    async def update_user_notifications(self, user_id, notify_lessons=None, notify_changes=None):
        if notify_lessons is not None:
            await self.execute("UPDATE users SET notify_lessons = ? WHERE user_id = ?", (notify_lessons, user_id))
        if notify_changes is not None:
            await self.execute("UPDATE users SET notify_changes = ? WHERE user_id = ?", (notify_changes, user_id))

    async def get_all_groups(self):
        groups = await self.execute("SELECT DISTINCT group_name FROM schedule", fetch='all')
        return [group[0] for group in groups] if groups else []

    async def get_schedule_for_group(self, group_name, day_of_week):
        return await self.execute("SELECT * FROM schedule WHERE group_name = ? AND day_of_week = ? ORDER BY time_start", (group_name, day_of_week), fetch='all')

    async def get_schedule_hash(self, file_hash):
        return await self.execute("SELECT file_hash FROM schedule_files WHERE file_hash = ?", (file_hash,), fetch='one')

    async def add_schedule_hash(self, file_hash):
        await self.execute("INSERT INTO schedule_files (file_hash) VALUES (?)", (file_hash,))

    async def clear_schedule_for_new_parse(self, new_file_hash):
        await self.execute("DELETE FROM schedule")
        await self.execute("DELETE FROM schedule_files")
        await self.add_schedule_hash(new_file_hash)
        logging.info("Старое расписание и хэши удалены из БД для новой записи.")

    async def save_schedule(self, lessons):
        query = "INSERT INTO schedule (group_name, day_of_week, date, lesson_number, time_start, time_end, subject, teacher, cabinet, file_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        params = [(l['group_name'], l['day_of_week'], l['date'], l['lesson_number'], l['time_start'], l['time_end'], l['subject'], l['teacher'], l['cabinet'], l['file_hash']) for l in lessons]
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.cursor()
            await cursor.executemany(query, params)
            await db.commit()
    
    async def update_user_reminder_settings(self, user_id, morning_time=None, lesson_reminder_minutes=None):
        """Update user's reminder time settings"""
        if morning_time is not None:
            await self.execute("UPDATE users SET morning_reminder_time = ? WHERE user_id = ?", (morning_time, user_id))
        if lesson_reminder_minutes is not None:
            await self.execute("UPDATE users SET lesson_reminder_minutes = ? WHERE user_id = ?", (lesson_reminder_minutes, user_id))
    
    async def get_users_for_morning_reminder(self):
        """Get all users who should receive morning reminders"""
        return await self.execute(
            "SELECT user_id, group_name, morning_reminder_time FROM users WHERE notify_lessons = TRUE AND group_name IS NOT NULL",
            fetch='all'
        )
    
    async def get_users_by_group(self, group_name):
        """Get all users in a specific group"""
        return await self.execute(
            "SELECT user_id FROM users WHERE group_name = ?",
            (group_name,),
            fetch='all'
        )
    
    async def get_all_users_with_notifications(self):
        """Get all users who have any notifications enabled"""
        return await self.execute(
            "SELECT user_id, group_name, notify_lessons, notify_changes FROM users WHERE (notify_lessons = TRUE OR notify_changes = TRUE) AND group_name IS NOT NULL",
            fetch='all'
        )