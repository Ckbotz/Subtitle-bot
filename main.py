#!/usr/bin/env python3
import logging
import threading
import sys
from bot import run_bot
from web_server import run_server
from subtitle_embedder import check_ffmpeg
from config import BOT_TOKEN, API_ID, API_HASH
from pyrogram import utils as pyroutils

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start both bot and web server"""
    
    # Check if credentials are set
    if BOT_TOKEN == 'your_bot_token_here':
        logger.error("BOT_TOKEN not set! Please set the BOT_TOKEN environment variable.")
        logger.error("Get your token from @BotFather on Telegram")
        sys.exit(1)
    
    if API_ID == 0 or API_HASH == 'your_api_hash_here':
        logger.error("API_ID and API_HASH not set!")
        logger.error("Get your API credentials from https://my.telegram.org/apps")
        sys.exit(1)
    
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        logger.error("FFmpeg is not installed or not in PATH!")
        logger.error("Please install FFmpeg before running the bot.")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Starting Telegram Subtitle Bot (Pyrogram Version)")
    logger.info("=" * 60)
    logger.info(f"API_ID: {API_ID}")
    logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
    logger.info("=" * 60)
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_server, daemon=True)
    web_thread.start()
    logger.info("✓ Web server started in background thread")
    
    # Start the bot (this will block)
    try:
        logger.info("✓ Starting Telegram bot...")
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
