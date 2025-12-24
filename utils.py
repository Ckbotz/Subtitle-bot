#!/usr/bin/env python3
"""
Utility functions for Subtitle Embedder Bot
"""

import logging
from config import Config

logger = logging.getLogger(__name__)

async def send_log(bot, user):
    """Send log message to log channel when new user starts bot"""
    if not Config.LOG_CHANNEL:
        return
    
    try:
        log_text = f"#NewUser\n\n"
        log_text += f"**User ID:** `{user.id}`\n"
        log_text += f"**Name:** {user.first_name}"
        if user.last_name:
            log_text += f" {user.last_name}"
        if user.username:
            log_text += f"\n**Username:** @{user.username}"
        
        await bot.send_message(
            chat_id=Config.LOG_CHANNEL,
            text=log_text
        )
    except Exception as e:
        logger.error(f"Error sending log: {e}")

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in Config.ADMINS

async def check_user_ban(db, user_id):
    """Check if user is banned"""
    ban_status = await db.get_ban_status(user_id)
    return ban_status['is_banned'], ban_status['ban_reason']

def format_caption(template, file_name, file_size):
    """Format caption with file details"""
    try:
        size_mb = file_size / (1024 * 1024)
        formatted = template.replace('{file_name}', file_name)
        formatted = formatted.replace('{file_size}', f"{size_mb:.2f} MB")
        return formatted
    except Exception as e:
        logger.error(f"Error formatting caption: {e}")
        return template
