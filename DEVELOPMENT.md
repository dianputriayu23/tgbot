# Development Guide

## Project Structure

```
tgbot/
├── config.py              # Configuration settings
├── main.py               # Entry point
├── database/             # Database layer
│   ├── __init__.py
│   └── db.py            # Database operations
├── handlers/             # Message and command handlers
│   ├── __init__.py
│   ├── common.py        # Common commands
│   └── schedule_viewer.py  # Schedule viewing
├── keyboards/            # Telegram keyboards
│   ├── __init__.py
│   ├── inline.py        # Inline keyboards
│   └── reply.py         # Reply keyboards
├── notifications/        # Notification system
│   └── __init__.py      # NotificationService
├── parser/              # Schedule parser
│   ├── __init__.py
│   └── parser.py        # XLSX file parser
├── scheduler/           # Task scheduler
│   ├── __init__.py
│   └── jobs.py          # Scheduled jobs
└── utils/               # Utilities
    ├── __init__.py
    └── states.py        # FSM states

## Testing

Run all tests:
```bash
python test_bot.py
python test_notifications.py
```

## Configuration

Edit `config.py` to modify:
- Schedule check interval
- Morning reminder time
- Timezone
- Parser settings
- Logging level

## Database Schema

### users table
- `user_id` (INTEGER PRIMARY KEY) - Telegram user ID
- `full_name` (TEXT) - User's full name
- `username` (TEXT) - Telegram username
- `education_form` (TEXT) - Education form (9_classes/11_classes)
- `course` (INTEGER) - Course number
- `group_name` (TEXT) - Group name
- `notify_lessons` (BOOLEAN) - Enable lesson notifications
- `notify_changes` (BOOLEAN) - Enable change notifications
- `morning_reminder_time` (TEXT) - Custom morning reminder time
- `lesson_reminder_minutes` (INTEGER) - Minutes before lesson to remind

### schedule table
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `group_name` (TEXT) - Group name
- `day_of_week` (TEXT) - Day of week in Russian
- `date` (TEXT) - Date
- `lesson_number` (TEXT) - Lesson number (I, II, III, etc.)
- `time_start` (TEXT) - Start time
- `time_end` (TEXT) - End time
- `subject` (TEXT) - Subject name
- `teacher` (TEXT) - Teacher name
- `cabinet` (TEXT) - Cabinet/room number
- `file_hash` (TEXT) - Hash of source file

### schedule_files table
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `file_name` (TEXT) - Original filename
- `file_hash` (TEXT UNIQUE) - SHA256 hash

## Key Features

### Parser
- **Dual-strategy parsing**: Uses calamine (fast) with XML fallback
- **Handles merged cells**: Fills merged cell values across all cells
- **Resilient to anomalies**: Handles empty rows, missing data, etc.
- **Auto-detection**: Finds headers and groups automatically

### Notifications
- **Morning reminders**: Customizable time per user
- **Change notifications**: Auto-notify when schedule updates
- **Lesson reminders**: Remind before lessons start (configurable)
- **Toggle per user**: Users can enable/disable each type

### Performance
- **Asynchronous I/O**: All operations are async
- **Database indexes**: Optimized queries
- **Connection pooling**: Via aiosqlite
- **Efficient parsing**: Two-strategy approach

## Adding New Features

### Adding a new handler
1. Create handler function in `handlers/`
2. Register router in `main.py`
3. Add keyboard buttons if needed in `keyboards/`

### Adding a new scheduled job
1. Add function in `scheduler/jobs.py`
2. Register with `scheduler.add_job()` in `setup_scheduler()`

### Adding a new notification type
1. Add method to `NotificationService` in `notifications/__init__.py`
2. Call from appropriate handler or scheduler

## Debugging

Enable debug logging:
```python
# In config.py
LOG_LEVEL = "DEBUG"
```

Check database content:
```bash
sqlite3 schedule.db
.tables
SELECT * FROM users;
SELECT * FROM schedule LIMIT 10;
```

## Common Issues

### Parser not finding schedule
- Check SCHEDULE_URL in config.py
- Verify website structure hasn't changed
- Check logs for download errors

### Notifications not sending
- Verify bot token in .env
- Check user has notifications enabled
- Verify scheduler is running

### Database locked errors
- Ensure only one bot instance is running
- Check file permissions on schedule.db

## Best Practices

1. **Always use async/await** for I/O operations
2. **Log important events** with appropriate level
3. **Handle exceptions** gracefully
4. **Test changes** before deploying
5. **Keep functions small** and focused
6. **Document complex logic** with comments
7. **Use type hints** where appropriate

## Deployment

1. Set up environment variables in `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run initial test: `python test_bot.py`
4. Start bot: `python main.py`
5. Monitor logs for errors

For production:
- Use systemd or supervisor to keep bot running
- Set up log rotation
- Monitor disk space for database
- Backup database regularly
