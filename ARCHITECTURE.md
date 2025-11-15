# System Architecture - PKEU Schedule Bot

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TELEGRAM USER                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT API                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MAIN.PY                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Aiogram 3.x Dispatcher                      │   │
│  │  - Bot Initialization                                    │   │
│  │  - Router Registration                                   │   │
│  │  - Middleware (Database Injection)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ HANDLERS │ │ DATABASE │ │ SCHEDULER│
└──────────┘ └──────────┘ └──────────┘
```

## Component Breakdown

### 1. Handlers Layer
```
handlers/
├── start.py         → User Registration Flow
│   └── FSM States:
│       ├── choosing_base (9/11)
│       ├── choosing_course (1/2/3)
│       └── choosing_group (from DB)
│
├── schedule.py      → Schedule Display
│   ├── Today
│   ├── Tomorrow
│   └── Weekday (Mon-Sat)
│
├── settings.py      → User Settings
│   ├── Change Group
│   ├── Toggle Notifications (Pairs)
│   ├── Toggle Notifications (Changes)
│   └── Toggle Notifications (Schedule)
│
├── profile.py       → User Profile
│   └── Display: ID, Group, Course, Notifications
│
└── help.py          → Help & Info
    ├── Commands List
    └── User Count
```

### 2. Database Layer
```
database/db.py → SQLite Operations

Tables:
┌─────────────────────────────────────────┐
│ USERS                                   │
├─────────────────────────────────────────┤
│ id, tg_id, education_base, course,      │
│ group_name, notifications_pairs,        │
│ notifications_changes, notifications_   │
│ schedule, created_at                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ GROUPS                                  │
├─────────────────────────────────────────┤
│ id, name, base, course, speciality      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ SCHEDULES                               │
├─────────────────────────────────────────┤
│ id, file_path, parse_date, groups_data  │
│ (JSON)                                  │
└─────────────────────────────────────────┘

Operations:
├── User CRUD
├── Group CRUD
├── Schedule CRUD
└── Notification Settings
```

### 3. Parser Layer
```
parser/parser.py → XLSX Processing

┌─────────────────────────────────────────┐
│ Schedule Website                        │
│ https://pkeu.ru/sites/default/files/   │
│ Files_up_page/                          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Download XLSX Files                     │
│ - Async download via aiohttp            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Parse with python-calamine              │
│ (Fallback: XML parsing)                 │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Extract Data:                           │
│ - Groups (Б1-25, БУ-25, etc.)          │
│ - Days (Monday-Saturday)                │
│ - Lessons (Time, Subject, Teacher, Room)│
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Store in Database                       │
└─────────────────────────────────────────┘
```

### 4. Scheduler Layer
```
scheduler/jobs.py → Automated Tasks

APScheduler Jobs:
├── check_schedule (Every 20 min)
│   └── Check for new schedule files
│
├── morning_notifications_1_3 (7:30)
│   └── Notify 1st & 3rd year students
│
├── morning_notifications_2 (10:00)
│   └── Notify 2nd year students
│
├── evening_notifications (18:00)
│   └── Notify about new schedules
│
└── cleanup_old_files (Daily 3:00)
    └── Delete files > 8 days old
```

### 5. Keyboards Layer
```
keyboards/
├── main.py
│   └── Main Navigation
│       ├── 📅 Сегодня
│       ├── 📆 Завтра
│       ├── Пн, Вт, Ср, Чт, Пт, Сб
│       ├── ⚙️ Настройки
│       ├── 👤 Профиль
│       └── ❓ Помощь
│
└── settings.py
    ├── Education Base Selector (9/11)
    ├── Course Selector (1/2/3)
    ├── Group Selector (Dynamic from DB)
    └── Settings Menu
```

## Data Flow

### User Registration Flow
```
User sends /start
    ↓
Check if user exists in DB
    ↓
No → Start Registration:
    ↓
Select Base (9/11) → FSM State: choosing_base
    ↓
Select Course (1/2/3) → FSM State: choosing_course
    ↓
Select Group → FSM State: choosing_group
    ↓
Save to Database
    ↓
Show Main Keyboard
```

### Schedule Display Flow
```
User clicks "Сегодня"
    ↓
Handler gets user from DB
    ↓
Get user's group_name
    ↓
Get latest schedule from DB
    ↓
Extract today's schedule for group
    ↓
Format with emoji and HTML
    ↓
Send to user
```

### Notification Flow
```
Scheduler triggers at set time
    ↓
Get all users with notifications_pairs=1
    ↓
Filter by course (1,3 for 7:30 / 2 for 10:00)
    ↓
For each user:
    ↓
Get today's schedule
    ↓
Format message
    ↓
Send notification
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│ Python 3.10+                            │
├─────────────────────────────────────────┤
│ ├── aiogram 3.13.1                      │
│ │   └── Modern async Telegram bot       │
│ │       framework                        │
│ ├── aiohttp 3.10.10                     │
│ │   └── Async HTTP requests              │
│ ├── python-calamine 0.2.3               │
│ │   └── Fast XLSX parsing                │
│ ├── apscheduler 3.10.4                  │
│ │   └── Job scheduling                   │
│ └── python-dotenv 1.0.1                 │
│     └── Environment configuration        │
└─────────────────────────────────────────┘
```

## File Storage

```
tgbot/
├── bot.db              → SQLite database
├── bot.log             → Application logs
├── .env                → Configuration (user creates)
└── schedules/          → Downloaded XLSX files
    ├── [date].xlsx
    └── [auto-deleted after 8 days]
```

## Security

- No hardcoded credentials
- Environment variables via .env
- SQLite with parameterized queries (SQL injection protection)
- Input validation on all user inputs
- Error handling throughout
- Logging for audit trail
- CodeQL scan: 0 vulnerabilities

## Scalability

**Current Implementation:**
- Single bot instance
- SQLite database
- Local file storage
- APScheduler for jobs

**Future Enhancements:**
- PostgreSQL for multi-instance support
- Redis for caching
- Celery for distributed task queue
- S3/MinIO for file storage
- Horizontal scaling with load balancer

## Performance

- Async I/O for all operations
- Database connection pooling
- Efficient XLSX parsing with calamine
- Scheduled tasks run independently
- No blocking operations in handlers

## Monitoring & Logging

```
Logs:
├── bot.log (File)
│   ├── INFO: Normal operations
│   ├── WARNING: Non-critical issues
│   └── ERROR: Critical problems
│
└── Console Output
    └── Real-time status updates
```

## Deployment Options

1. **Local Server**
   - Simple `python main.py`
   - Good for testing/development

2. **Linux Server (systemd)**
   - Create systemd service
   - Auto-restart on failure
   - Production recommended

3. **Docker**
   - Containerized deployment
   - Easy scaling
   - Isolated environment

4. **Cloud Services**
   - Heroku, Railway, Render
   - Zero infrastructure management
   - Built-in monitoring

## Maintenance

**Daily:**
- Check bot.log for errors
- Monitor user count

**Weekly:**
- Review notification delivery
- Check schedule updates

**Monthly:**
- Database backup
- Update dependencies
- Review user feedback

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-11-15  
**Status:** Production Ready ✅
