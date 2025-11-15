# Quick Start Guide

Get your Telegram Schedule Bot up and running in 5 minutes!

## Prerequisites
- Python 3.9 or higher
- Internet connection
- Telegram account

## Step 1: Get Your Bot Token (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts:
   - Choose a name for your bot (e.g., "PKEU Schedule Bot")
   - Choose a username (must end in 'bot', e.g., "pkeu_schedule_bot")
4. **Copy the token** that BotFather gives you (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Configure the Bot (1 minute)

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/dianputriayu23/tgbot.git
cd tgbot

# Create your configuration file
cp .env.example .env

# Edit the .env file and add your token
nano .env  # or use any text editor
```

In the `.env` file, replace `your_bot_token_here` with your actual token:
```
API_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=your_telegram_id
```

To get your Telegram ID, send a message to @userinfobot

## Step 3: Run the Bot (2 minutes)

### Option A: Using the run script (easiest)
```bash
chmod +x run.sh
./run.sh
```

### Option B: Manual setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

## Step 4: Test Your Bot

1. Open Telegram
2. Search for your bot username (the one you created in Step 1)
3. Send `/start`
4. Follow the registration process:
   - Choose education base (9 or 11 classes)
   - Select your course
   - Select your group
5. Try viewing schedule:
   - Click "Сегодня" for today's schedule
   - Click "Завтра" for tomorrow's schedule
   - Click any day of the week

## That's It! 🎉

Your bot is now running and ready to use!

## What's Next?

### For Development & Testing
- Read [TESTING.md](TESTING.md) for comprehensive testing
- Check logs for any errors
- Test all features listed in [FEATURES.md](FEATURES.md)

### For Production Deployment
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Set up systemd service for 24/7 operation
- Configure monitoring and backups
- Review security best practices

## Troubleshooting

### Bot doesn't respond to /start
- ✅ Check if bot is running: `ps aux | grep main.py`
- ✅ Verify token in .env is correct
- ✅ Check for error messages in the console
- ✅ Make sure you're messaging the correct bot

### "No groups found" error
- ✅ Wait a few minutes for initial schedule download
- ✅ Check internet connection
- ✅ Verify pkeu.ru is accessible
- ✅ Check logs for parser errors

### Schedule not showing
- ✅ Verify you completed registration
- ✅ Check if schedule.db file exists
- ✅ Look for errors in logs
- ✅ Try re-registering with /start

### Dependencies won't install
- ✅ Update pip: `pip install --upgrade pip`
- ✅ Check Python version: `python3 --version` (need 3.9+)
- ✅ Install system dependencies: `sudo apt-get install python3-dev`

## Need Help?

- 📚 Check the full [README.md](README.md)
- 🧪 Review [TESTING.md](TESTING.md) for testing procedures
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- ✅ Verify [FEATURES.md](FEATURES.md) for feature list

## Commands Reference

| Command | Description |
|---------|-------------|
| Сегодня | Today's schedule |
| Завтра | Tomorrow's schedule |
| Понедельник...Суббота | Specific day's schedule |
| Настройки | View/change settings |
| Помощь | Help and user count |

## Stopping the Bot

Press `Ctrl+C` in the terminal where the bot is running.

For background processes:
```bash
# Find the process
ps aux | grep main.py

# Kill the process
kill <PID>
```

Enjoy your automated schedule bot! 🤖📅
