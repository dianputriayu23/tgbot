@echo off
setlocal

REM --- Устанавливаем абсолютный путь к папке со скриптом ---
set "CURRENT_DIR=%~dp0"
set "VENV_PYTHON=%CURRENT_DIR%venv\Scripts\python.exe"
set "VENV_PIP=%CURRENT_DIR%venv\Scripts\pip.exe"

echo [INFO] Python executable to be used: %VENV_PYTHON%
echo.

REM --- Шаг 1: Создание виртуального окружения, если его нет ---
if not exist "%CURRENT_DIR%venv" (
    echo [STEP 1/4] Creating virtual environment...
    py -3 -m venv venv
) else (
    echo [STEP 1/4] Virtual environment already exists.
)

REM --- Шаг 2: Установка зависимостей с использованием АБСОЛЮТНОГО пути к pip ---
echo.
echo [STEP 2/4] Installing all required dependencies using the correct pip...
"%VENV_PIP%" install -r requirements.txt

REM --- Шаг 3: Удаление старой базы данных для чистого старта ---
echo.
echo [STEP 3/4] Deleting old database file (if exists)...
if exist "%CURRENT_DIR%schedule.db" (
    del "%CURRENT_DIR%schedule.db"
)

REM --- Шаг 4: Запуск бота с использованием АБСОЛЮТНОГО пути к python ---
echo.
echo [STEP 4/4] Starting the bot using the correct python executable...
echo =================================================================
"%VENV_PYTHON%" main.py

echo.
echo =================================================================
echo --- Bot has stopped. Press any key to close. ---
pause
endlocal