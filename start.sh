#!/bin/bash

# Telegram Bot Startup Script

echo "🤖 Запуск Telegram-бота для расписания колледжа..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
fi

# Activate virtual environment
echo "🔄 Активация виртуального окружения..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python3.*/site-packages/aiogram/__init__.py" ]; then
    echo "📦 Установка зависимостей..."
    pip install -r requirements.txt
    echo "✅ Зависимости установлены"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env со следующим содержимым:"
    echo "API_TOKEN=ваш_токен_бота"
    echo "ADMIN_ID=ваш_telegram_id"
    exit 1
fi

# Create necessary directories
mkdir -p downloads data

echo "✅ Проверка завершена"
echo "🚀 Запуск бота..."
python main.py
