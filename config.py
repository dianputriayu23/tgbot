"""
Configuration settings for the Telegram bot
"""

# Schedule URL
SCHEDULE_URL = "https://pkeu.ru/raspisanie-zanyatiy"
BASE_URL = "https://pkeu.ru"

# Directories
DOWNLOADS_DIR = "downloads"

# Scheduler settings
SCHEDULE_CHECK_INTERVAL_MINUTES = 30

# Notification settings
DEFAULT_MORNING_REMINDER_TIME = "07:30"
DEFAULT_LESSON_REMINDER_MINUTES = 30

# Timezone
TIMEZONE = "Asia/Yekaterinburg"

# Database
DATABASE_NAME = "schedule.db"

# Parser settings
PARSER_MAX_RETRIES = 3
PARSER_RETRY_DELAY_SECONDS = 5

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# Russian day names
DAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

# Course year calculation
# The year in group name (e.g., 24 in БУ1-24) represents admission year
# Course is calculated as: current_year_short - admission_year + 1
# If current month >= 9 (September), add 1 to course
