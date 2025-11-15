# Quick Deployment Guide

## Prerequisites
- Python 3.12 or higher
- Telegram Bot Token (from @BotFather)
- Server or local machine to run the bot

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/dianputriayu23/tgbot.git
cd tgbot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file:
```
API_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_ID=YOUR_TELEGRAM_USER_ID
```

To get your Telegram User ID:
1. Start a chat with @userinfobot
2. It will send you your ID

### 5. Test the Installation
```bash
python test_bot.py
python test_notifications.py
```

Both should show "✅ ALL TESTS PASSED!"

### 6. Run the Bot
```bash
python main.py
```

You should see:
```
INFO - Database initialized.
INFO - Command handlers registered.
INFO - Performing initial schedule check on startup...
INFO - Scheduler has been started.
INFO - Bot is starting polling...
```

### 7. Test in Telegram
1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Follow the registration process

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/tgbot.service`:
```ini
[Unit]
Description=Telegram Schedule Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/tgbot
Environment="PATH=/path/to/tgbot/venv/bin"
ExecStart=/path/to/tgbot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
sudo systemctl status tgbot
```

View logs:
```bash
sudo journalctl -u tgbot -f
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t tgbot .
docker run -d --name tgbot --env-file .env --restart unless-stopped tgbot
```

## Configuration

Edit `config.py` to customize:
- `SCHEDULE_CHECK_INTERVAL_MINUTES` - How often to check for updates
- `DEFAULT_MORNING_REMINDER_TIME` - Morning reminder time
- `TIMEZONE` - Your timezone
- `SCHEDULE_URL` - Schedule source URL

## Monitoring

### Check Bot Status
```bash
# Systemd
sudo systemctl status tgbot

# Docker
docker logs -f tgbot
```

### Check Database
```bash
sqlite3 schedule.db
.tables
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM schedule;
.exit
```

### Monitor Logs
Logs include:
- Database operations
- Schedule parsing
- Notifications sent
- Errors and exceptions

## Backup

### Database Backup
```bash
# Create backup
cp schedule.db schedule.db.backup

# Automated backup (add to crontab)
0 0 * * * cp /path/to/tgbot/schedule.db /path/to/backups/schedule-$(date +\%Y\%m\%d).db
```

## Troubleshooting

### Bot not responding
1. Check bot is running: `systemctl status tgbot`
2. Check logs for errors: `journalctl -u tgbot -n 50`
3. Verify API token in `.env`
4. Test network connectivity

### Schedule not updating
1. Check schedule URL in `config.py`
2. Verify website is accessible
3. Check parser logs for errors
4. Test manually: `python -c "from parser.parser import download_latest_schedule_file; import asyncio; print(asyncio.run(download_latest_schedule_file()))"`

### Database locked
1. Ensure only one instance is running
2. Check file permissions on `schedule.db`
3. Restart the bot

### Notifications not sent
1. Verify users have enabled notifications
2. Check scheduler is running (look for "Morning reminder sent" in logs)
3. Verify bot has permission to message users

## Updating

```bash
cd /path/to/tgbot
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart tgbot
```

## Security

- Never commit `.env` file
- Keep API token secret
- Regular security updates: `pip install --upgrade`
- Monitor logs for suspicious activity
- Backup database regularly

## Performance Tips

1. **For many users (1000+)**:
   - Consider PostgreSQL instead of SQLite
   - Use Redis for session storage
   - Deploy multiple instances behind load balancer

2. **Monitor resource usage**:
   ```bash
   # CPU and memory
   top -p $(pgrep -f main.py)
   
   # Database size
   du -h schedule.db
   ```

3. **Optimize database**:
   ```bash
   sqlite3 schedule.db "VACUUM;"
   ```

## Support

- Check logs first: `journalctl -u tgbot -n 100`
- Review documentation: README.md, DEVELOPMENT.md
- Test components: `python test_bot.py`

## Next Steps

After deployment:
1. Monitor logs for first 24 hours
2. Test notifications
3. Verify schedule updates work
4. Get user feedback
5. Plan enhancements

---

For detailed development guide, see [DEVELOPMENT.md](DEVELOPMENT.md)
For user guide, see [USER_GUIDE.md](USER_GUIDE.md)
