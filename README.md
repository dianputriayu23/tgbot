# Telegram Schedule Bot for Perm College of Economics and Management

A Telegram bot for viewing college schedules with automatic updates and notifications.

## Features

- 📅 View schedule for today, tomorrow, or any day of the week
- 🔔 Automatic morning notifications (07:30 for courses 1,3 and 10:00 for course 2)
- 🌙 Evening notifications at 20:00 with tomorrow's schedule
- 🔄 Automatic schedule updates every 30 minutes from pkeu.ru
- 👥 User registration with group selection
- ⚙️ Customizable notification settings
- 📊 Support for both 9-class and 11-class education bases

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dianputriayu23/tgbot.git
cd tgbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your bot token:
```
API_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
```

5. Run the bot:
```bash
python main.py
```

## Project Structure

```
tgbot/
├── database/       # Database management
├── handlers/       # Message and callback handlers
├── keyboards/      # Inline and reply keyboards
├── parser/         # XLSX schedule parser
├── scheduler/      # Background jobs for notifications
├── utils/          # States and utilities
├── main.py         # Entry point
└── requirements.txt
```

## Usage

1. Start the bot with `/start`
2. Select your education base (9 or 11 classes)
3. Choose your course and group
4. View schedule using buttons or commands
5. Configure notifications in Settings

## Commands

- Сегодня - Today's schedule
- Завтра - Tomorrow's schedule
- Понедельник...Суббота - Schedule for specific day
- Настройки - Settings
- Помощь - Help

## Technologies

- aiogram 3.13.1 - Telegram Bot API framework
- aiosqlite - Async SQLite database
- APScheduler - Background job scheduler
- python-calamine - Fast XLSX parser
- BeautifulSoup4 - HTML parsing
- lxml - XML parsing

## License

MIT License
