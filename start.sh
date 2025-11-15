#!/bin/bash
# Startup script for Telegram Schedule Bot

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Telegram Schedule Bot Startup${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env and add your BOT_TOKEN${NC}"
    echo -e "${YELLOW}Then run this script again${NC}"
    exit 1
fi

# Check if BOT_TOKEN is set
if grep -q "your_bot_token_here" .env; then
    echo -e "${RED}Error: BOT_TOKEN not configured in .env${NC}"
    echo -e "${YELLOW}Please edit .env and add your real BOT_TOKEN${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    exit 1
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Starting bot...${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Start the bot
python3 main.py
