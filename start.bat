@echo off
REM Telegram Bot Startup Script for Windows

echo 🤖 Запуск Telegram-бота для расписания колледжа...

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Виртуальное окружение не найдено!
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    echo ✅ Виртуальное окружение создано
)

REM Activate virtual environment
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ❌ Файл .env не найден!
    echo Создайте файл .env со следующим содержимым:
    echo API_TOKEN=ваш_токен_бота
    echo ADMIN_ID=ваш_telegram_id
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Проверка зависимостей...
pip install -r requirements.txt >nul 2>&1

REM Create necessary directories
if not exist "downloads\" mkdir downloads
if not exist "data\" mkdir data

echo ✅ Проверка завершена
echo 🚀 Запуск бота...
python main.py

pause
