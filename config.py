import os
from pathlib import Path

# Telegram API credentials
API_ID = int(os.environ.get('API_ID', '0'))
API_HASH = os.environ.get('API_HASH', 'your_api_hash_here')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your_bot_token_here')

# Web server configuration
WEB_SERVER_PORT = int(os.environ.get('PORT', 8080))
WEB_SERVER_HOST = os.environ.get('HOST', '0.0.0.0')

# Directory configuration
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / 'downloads'
OUTPUT_DIR = BASE_DIR / 'output'
SESSION_DIR = BASE_DIR / 'sessions'

# Create directories if they don't exist
DOWNLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)

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
BOT_VERSION = "2.0.0 (Pyrogram)"
