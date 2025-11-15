# Testing Guide

## Manual Testing Checklist

### 1. Initial Setup
- [ ] Bot starts without errors
- [ ] Database file (schedule.db) is created
- [ ] Downloads directory is created
- [ ] No error messages in logs

### 2. User Registration Flow
- [ ] `/start` command works
- [ ] Inline keyboard appears with "9 классов" and "11 классов"
- [ ] After selecting education base, course selection appears
  - [ ] 9 classes: shows courses 1-4
  - [ ] 11 classes: shows courses 1-2
- [ ] After selecting course, group list appears
  - [ ] Groups are filtered correctly by course
  - [ ] Groups match the selected education base format
- [ ] After selecting group, confirmation message appears
- [ ] Main menu keyboard appears with all buttons
- [ ] User data is saved in database
- [ ] Static ID is generated automatically

### 3. Schedule Viewing
Test each button:
- [ ] **Сегодня** - Shows today's schedule
- [ ] **Завтра** - Shows tomorrow's schedule
- [ ] **Понедельник** - Shows Monday's schedule
- [ ] **Вторник** - Shows Tuesday's schedule
- [ ] **Среда** - Shows Wednesday's schedule
- [ ] **Четверг** - Shows Thursday's schedule
- [ ] **Пятница** - Shows Friday's schedule
- [ ] **Суббота** - Shows Saturday's schedule

Verify schedule format:
- [ ] Day name and date shown correctly
- [ ] Emoji numbers displayed (1️⃣, 2️⃣, etc.)
- [ ] Subject name shown
- [ ] Time displayed (e.g., "08:30-10:05")
- [ ] Teacher name shown (if available)
- [ ] Cabinet/room shown (if available)
- [ ] Resource link shown (if available)
- [ ] Empty days show "Пар нет..." message
- [ ] Sunday shows appropriate message

### 4. Settings
- [ ] Settings button opens profile
- [ ] Profile shows:
  - [ ] Static ID
  - [ ] Course number
  - [ ] Group name
  - [ ] Notification status for schedule
  - [ ] Notification status for changes
- [ ] "Сменить группу" button works
  - [ ] Returns to education base selection
  - [ ] Can re-register with new group
- [ ] Notification toggles work
  - [ ] Schedule notifications toggle on/off
  - [ ] Change notifications toggle on/off
  - [ ] Status updates immediately

### 5. Help Command
- [ ] Help button shows commands description
- [ ] User count is displayed
- [ ] All features are listed

### 6. Parser & Scheduler

#### Parser
- [ ] Bot downloads schedule from pkeu.ru on startup
- [ ] XLSX file is saved to downloads/
- [ ] File is parsed successfully
- [ ] Lessons are saved to database
- [ ] Groups are extracted correctly
- [ ] Merged cells are handled
- [ ] Both calamine and XML fallback work

#### Scheduler Jobs
- [ ] Schedule check runs every 30 minutes
- [ ] Old files (>8 days) are deleted
- [ ] Morning notifications (if time is right):
  - [ ] 07:30 - Courses 1 and 3 receive notifications
  - [ ] 10:00 - Course 2 receives notifications
- [ ] Evening notifications at 20:00:
  - [ ] All users receive tomorrow's schedule
- [ ] Change notifications:
  - [ ] Users notified when schedule changes
  - [ ] Only affected groups receive notifications

### 7. Edge Cases
- [ ] Multiple users can use bot simultaneously
- [ ] Users can change groups multiple times
- [ ] Invalid group selection is handled
- [ ] Network errors don't crash bot
- [ ] Database errors are logged
- [ ] Parser handles malformed XLSX files
- [ ] Notifications work with empty schedules
- [ ] Sunday is handled correctly (no classes)

### 8. Performance
- [ ] Bot responds quickly (< 1 second for most commands)
- [ ] Parser completes within reasonable time
- [ ] Database queries are fast
- [ ] Multiple users don't slow down the bot
- [ ] Memory usage is reasonable

### 9. Security
- [ ] .env file is not committed
- [ ] Bot token is not exposed in logs
- [ ] SQL injection is prevented (using parameterized queries)
- [ ] No sensitive user data is logged
- [ ] File permissions are appropriate

## Automated Testing

### Unit Tests
```bash
# TODO: Add unit tests for:
# - Database operations
# - Parser functions
# - Schedule formatting
# - Group detection logic
```

### Integration Tests
```bash
# TODO: Add integration tests for:
# - Complete registration flow
# - Schedule viewing with mock data
# - Notification sending
```

## Testing with Different Scenarios

### Test User Profiles
Create test users with different profiles:
1. User on 9 classes, course 1
2. User on 9 classes, course 2
3. User on 9 classes, course 3
4. User on 11 classes, course 1
5. User on 11 classes, course 2

### Test Schedule Scenarios
1. Empty schedule (no classes)
2. Full schedule (all days)
3. Partial schedule (some days)
4. Schedule with resource links
5. Schedule with special characters

### Test Notification Scenarios
1. User with all notifications enabled
2. User with only schedule notifications
3. User with only change notifications
4. User with all notifications disabled

## Debugging

### Check Logs
```bash
# If using systemd
sudo journalctl -u tgbot -f

# If running manually
# Logs appear in console
```

### Common Issues

**Bot doesn't respond:**
- Check if bot is running: `ps aux | grep main.py`
- Check bot token in .env
- Check internet connection
- Look for errors in logs

**Schedule not showing:**
- Check if schedule.db exists and has data
- Verify parser ran successfully
- Check group name matches database
- Look for parser errors in logs

**Notifications not working:**
- Verify scheduler is running
- Check notification settings for user
- Verify timezone is correct (Asia/Yekaterinburg)
- Check for errors in notification jobs

**Parser failing:**
- Verify pkeu.ru is accessible
- Check XLSX file format
- Try both calamine and XML parsing
- Check for network errors

### Database Inspection
```bash
# Install sqlite3 if needed
sudo apt-get install sqlite3

# Open database
sqlite3 schedule.db

# Useful queries
.tables
SELECT * FROM users;
SELECT COUNT(*) FROM schedule;
SELECT DISTINCT group_name FROM schedule;
SELECT * FROM schedule WHERE group_name = 'БУ-25' LIMIT 10;
.quit
```

## Load Testing
Test with multiple users:
```bash
# Simulate multiple users
# TODO: Create load testing script
```

## Final Checklist Before Deployment
- [ ] All manual tests pass
- [ ] No errors in logs during testing
- [ ] .env file configured correctly
- [ ] Database is working
- [ ] Parser successfully downloads and parses schedules
- [ ] Notifications are configured
- [ ] Documentation is complete
- [ ] Backups are set up
- [ ] Monitoring is in place
