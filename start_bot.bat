@echo off
chcp 65001 >nul
echo ================================================
echo     TELEGRAM БОТ РАСПИСАНИЯ PKEU
echo ================================================
echo.

cd /d %~dp0

if not exist "venv\" (
    echo [1/3] Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: Не удалось создать виртуальное окружение
        echo Убедитесь, что Python установлен и добавлен в PATH
        pause
        exit /b 1
    )
)

echo [2/3] Активация виртуального окружения...
call venv\Scripts\activate
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

if not exist "venv\Scripts\aiogram.exe" (
    echo [3/3] Установка зависимостей (первый запуск)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить зависимости
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo.
    echo ================================================
    echo ВНИМАНИЕ: Файл .env не найден!
    echo ================================================
    echo.
    echo Пожалуйста:
    echo 1. Скопируйте файл .env.example в .env
    echo 2. Откройте .env и укажите ваш токен бота
    echo 3. Запустите скрипт снова
    echo.
    pause
    exit /b 1
)

echo.
echo [✓] Запуск бота...
echo ================================================
echo Для остановки нажмите Ctrl+C
echo ================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo ОШИБКА: Бот остановлен с ошибкой
    echo ================================================
    echo.
    pause
)
