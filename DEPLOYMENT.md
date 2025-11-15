# Deployment Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Internet connection for downloading dependencies
- Telegram Bot Token (from @BotFather)

## Quick Start

1. **Get Bot Token**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Configure the Bot**
   ```bash
   cp .env.example .env
   nano .env  # or use any text editor
   ```
   
   Add your bot token and admin ID:
   ```
   API_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_id
   ```

3. **Run the Bot**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

## Running in Production

### Using systemd (Linux)

Create `/etc/systemd/system/tgbot.service`:

```ini
[Unit]
Description=Telegram Schedule Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/tgbot
ExecStart=/path/to/tgbot/venv/bin/python /path/to/tgbot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
sudo systemctl status tgbot
```

### Using PM2 (Node.js process manager)

```bash
npm install -g pm2
pm2 start main.py --name tgbot --interpreter python3
pm2 save
pm2 startup
```

### Using Screen (Simple method)

```bash
screen -S tgbot
cd /path/to/tgbot
./run.sh
# Press Ctrl+A then D to detach
```

To reattach:
```bash
screen -r tgbot
```

## Monitoring

### View Logs

With systemd:
```bash
sudo journalctl -u tgbot -f
```

With PM2:
```bash
pm2 logs tgbot
```

### Check Bot Status

With systemd:
```bash
sudo systemctl status tgbot
```

With PM2:
```bash
pm2 status
```

## Updating

1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```

3. Restart the bot:
   ```bash
   sudo systemctl restart tgbot  # or pm2 restart tgbot
   ```

## Troubleshooting

### Bot doesn't start
- Check if .env file exists and contains valid token
- Verify Python version: `python3 --version`
- Check logs for error messages

### Bot doesn't respond
- Verify internet connection
- Check if bot token is valid
- Ensure bot is running: `ps aux | grep main.py`

### Schedule not updating
- Check downloads/ directory permissions
- Verify pkeu.ru website is accessible
- Check logs for parser errors

### Database errors
- Delete schedule.db and restart (will reset all data)
- Check file permissions

## Security Notes

- Never commit .env file with real tokens
- Keep .gitignore updated
- Regularly update dependencies
- Monitor bot for unusual activity
- Set appropriate file permissions (chmod 600 .env)

## Backup

Important files to backup:
- `schedule.db` - User data and schedules
- `.env` - Configuration (securely)

```bash
# Backup database
cp schedule.db schedule.db.backup

# Automated backup with cron
0 2 * * * cp /path/to/tgbot/schedule.db /path/to/backups/schedule.db.$(date +\%Y\%m\%d)
```
