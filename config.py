#!/usr/bin/env python3
"""
Configuration file for Subtitle Embedder Bot
Enhanced with all necessary settings
"""

import os
from pathlib import Path

# Telegram API credentials
API_ID = int(os.environ.get('API_ID', '0'))
API_HASH = os.environ.get('API_HASH', 'your_api_hash_here')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your_bot_token_here')

# MongoDB Configuration
DB_URL = os.environ.get("DB_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "subtitle_bot")

# Admin Configuration (comma-separated user IDs)
ADMINS = [int(x) for x in os.environ.get("ADMINS", "0").split(",") if x.strip() and x != "0"]

# Log Channel (optional - for user join logs)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0")) if os.environ.get("LOG_CHANNEL") else None

# Web server configuration
WEB_SERVER_PORT = int(os.environ.get('PORT', 8080))
WEB_SERVER_HOST = os.environ.get('HOST', '0.0.0.0')

# Directory configuration
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / 'downloads'
OUTPUT_DIR = BASE_DIR / 'output'
SESSION_DIR = BASE_DIR / 'sessions'
THUMB_DIR = BASE_DIR / 'thumbnails'

# Create directories if they don't exist
DOWNLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

# FFmpeg configuration
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'ffmpeg')

# File size limits (in bytes)
MAX_VIDEO_SIZE = 4 * 1024 * 1024 * 1024  # 4GB (Pyrogram supports up to 4GB)
MAX_SUBTITLE_SIZE = 10 * 1024 * 1024  # 10MB

# Telegram API limits (Pyrogram can handle larger files)
TELEGRAM_MAX_FILE_SIZE = 4000 * 1024 * 1024  # 4000MB (4GB)

# Logging configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Bot information
BOT_NAME = "Subtitle Embedder Bot"
BOT_VERSION = "2.0.0 (Pyrogram - Integrated)"

# Config class for compatibility with database and admin panel
class Config:
    # Telegram API
    API_ID = API_ID
    API_HASH = API_HASH
    BOT_TOKEN = BOT_TOKEN
    
    # Database
    DB_URL = DB_URL
    DB_NAME = DB_NAME
    
    # Admin
    ADMINS = ADMINS
    LOG_CHANNEL = LOG_CHANNEL
    
    # Directories
    DOWNLOAD_DIR = DOWNLOAD_DIR
    OUTPUT_DIR = OUTPUT_DIR
    SESSION_DIR = SESSION_DIR
    THUMB_DIR = THUMB_DIR
    
    # FFmpeg
    FFMPEG_PATH = FFMPEG_PATH
    
    # File Limits
    MAX_VIDEO_SIZE = MAX_VIDEO_SIZE
    MAX_SUBTITLE_SIZE = MAX_SUBTITLE_SIZE
    TELEGRAM_MAX_FILE_SIZE = TELEGRAM_MAX_FILE_SIZE
    
    # Web Server
    WEB_SERVER_PORT = WEB_SERVER_PORT
    WEB_SERVER_HOST = WEB_SERVER_HOST
    
    # Logging
    LOG_LEVEL = LOG_LEVEL
    
    # Bot Info
    BOT_NAME = BOT_NAME
    BOT_VERSION = BOT_VERSION
