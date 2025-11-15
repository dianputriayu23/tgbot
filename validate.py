#!/usr/bin/env python3
"""
Test script to validate all bot components.
Run this before starting the bot to ensure everything is configured correctly.
"""

import sys
import os
from pathlib import Path
import asyncio


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")


def check_python_version():
    """Check if Python version is 3.10+"""
    print_header("Checking Python Version")
    version = sys.version_info
    print_info(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print_success("Python version OK")
        return True
    else:
        print_error("Python 3.10+ required")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print_header("Checking Dependencies")
    
    required_packages = [
        'telegram',
        'aiosqlite',
        'openpyxl',
        'pandas',
        'dotenv',
        'apscheduler'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing.append(package)
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print_info("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and is configured."""
    print_header("Checking Configuration")
    
    if not Path('.env').exists():
        print_error(".env file not found")
        print_info("Run: cp .env.example .env")
        print_info("Then edit .env and add your BOT_TOKEN")
        return False
    
    print_success(".env file exists")
    
    # Check if BOT_TOKEN is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_bot_token_here' in content:
            print_error("BOT_TOKEN not configured")
            print_info("Edit .env and add your real BOT_TOKEN")
            return False
        elif 'BOT_TOKEN=' not in content:
            print_error("BOT_TOKEN not found in .env")
            return False
    
    print_success("BOT_TOKEN configured")
    return True


def check_schedule_files():
    """Check if schedule files exist."""
    print_header("Checking Schedule Files")
    
    xlsx_files = list(Path('.').glob('*.xlsx'))
    xlsx_files = [f for f in xlsx_files if not f.name.startswith('~')]
    
    if xlsx_files:
        print_success(f"Found {len(xlsx_files)} schedule files")
        for f in xlsx_files[:5]:  # Show first 5
            print_info(f"  - {f.name}")
        if len(xlsx_files) > 5:
            print_info(f"  ... and {len(xlsx_files) - 5} more")
        return True
    else:
        print_error("No schedule files found")
        print_info("Add .xlsx files to the project folder")
        return False


async def test_modules():
    """Test that all modules can be imported and work."""
    print_header("Testing Modules")
    
    try:
        from database import Database
        print_success("Database module loaded")
        
        # Test database
        db = Database('test_validation.db')
        await db.connect()
        await db.initialize()
        await db.add_user(1, 'test', 'Test', 'User')
        await db.close()
        os.remove('test_validation.db')
        print_success("Database operations OK")
        
    except Exception as e:
        print_error(f"Database error: {e}")
        return False
    
    try:
        from parser import ScheduleParser
        print_success("Parser module loaded")
        
        # Test parser
        parser = ScheduleParser()
        files = parser.find_schedule_files('.')
        if files:
            print_success(f"Parser found {len(files)} files")
        else:
            print_info("No files to parse (this is OK)")
        
    except Exception as e:
        print_error(f"Parser error: {e}")
        return False
    
    try:
        from keyboards import get_main_keyboard
        print_success("Keyboards module loaded")
    except Exception as e:
        print_error(f"Keyboards error: {e}")
        return False
    
    try:
        from handlers import get_start_conversation_handler
        print_success("Handlers module loaded")
    except Exception as e:
        print_error(f"Handlers error: {e}")
        return False
    
    try:
        from scheduler import ScheduleJobManager
        print_success("Scheduler module loaded")
    except Exception as e:
        print_error(f"Scheduler error: {e}")
        return False
    
    return True


def check_directory_structure():
    """Check if all required directories exist."""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        'database',
        'parser',
        'handlers',
        'keyboards',
        'scheduler'
    ]
    
    all_exist = True
    for dirname in required_dirs:
        if Path(dirname).exists():
            print_success(f"{dirname}/ directory exists")
        else:
            print_error(f"{dirname}/ directory not found")
            all_exist = False
    
    return all_exist


async def main():
    """Run all validation checks."""
    print("\n" + "=" * 60)
    print("  TELEGRAM BOT VALIDATION")
    print("=" * 60)
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Configuration': check_env_file(),
        'Directory Structure': check_directory_structure(),
        'Schedule Files': check_schedule_files(),
    }
    
    # Async checks
    checks['Module Tests'] = await test_modules()
    
    print_header("Validation Summary")
    
    all_passed = True
    for check_name, passed in checks.items():
        if passed:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print_success("ALL CHECKS PASSED!")
        print_info("You can now run the bot with: python main.py")
    else:
        print_error("SOME CHECKS FAILED")
        print_info("Please fix the issues above before running the bot")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
