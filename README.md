# Telegram Bot - College Schedule Viewer

A full-featured Telegram bot for viewing the Perm College of Economics and Management schedule.

## 🌟 Features

- **Schedule Parser**: Automatic parsing of XLSX files from the college website
- **Smart Notifications**: Time-based reminders and change alerts
- **User-Friendly Interface**: Interactive menus and beautiful formatting
- **Multi-Course Support**: Handles both 9 and 11-year education bases
- **Database**: SQLite storage for users and schedules

## 📖 Documentation

See [README_RU.md](README_RU.md) for full documentation in Russian.

## 🚀 Quick Start

### Linux/Mac
```bash
./start.sh
```

### Windows
```batch
start.bat
```

### Manual Start
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your bot token

# Run the bot
python main.py
```

## 📋 Requirements

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Internet connection

## 📁 Project Structure

```
tgbot/
├── database/          # Database module
├── handlers/          # Command handlers
├── keyboards/         # Bot keyboards
├── parser/            # Schedule parser
├── scheduler/         # Task scheduler
├── utils/             # Utilities
├── main.py           # Entry point
└── requirements.txt  # Dependencies
```

## 🔒 Security

The bot uses secure practices:
- Environment variables for sensitive data
- SQLite for local data storage
- No hardcoded credentials

## 📝 License

MIT License

## 👥 Author

Created for Perm College of Economics and Management.