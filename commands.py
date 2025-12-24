#!/usr/bin/env python3
"""
Commands handler for Subtitle Embedder Bot
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from utils import is_admin, send_log
from config import THUMB_DIR
import os

logger = logging.getLogger(__name__)

@filters.create
def admin_filter(_, __, message):
    """Filter for admin-only commands"""
    return is_admin(message.from_user.id)

async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Add user to database
    is_new = await db.add_user(user_id)
    
    # Send log if new user
    if is_new:
        await send_log(client, message.from_user)
    
    welcome_message = """
🎬 **Subtitle Embedder Bot**

Welcome! I can embed subtitles into your video files.

**How to use:**
1. Send me a video file
2. Send subtitle file(s) - you can send multiple
3. Select language for each subtitle
4. Send /done when you've sent all subtitles
5. I'll process and send back your video with embedded subtitles

**Supported formats:**
📹 Video: MP4, MKV, AVI, MOV, etc.
📝 Subtitles: SRT, ASS, SSA, VTT, SUB

**Commands:**
/start - Start the bot
/help - Show help message
/cancel - Cancel current operation

**Customization:**
/set_caption - Set custom caption
/see_caption - View your caption
/del_caption - Delete custom caption
/view_thumb - View your thumbnail
/del_thumb - Delete your thumbnail

**Features:**
✨ Supports files up to 4GB
✨ Multiple subtitle tracks
✨ Preserves video quality
✨ Custom thumbnails
✨ Custom captions
✨ Manual language selection
"""
    await message.reply_text(welcome_message)

async def help_command(client: Client, message: Message):
    """Handle /help command"""
    await start_command(client, message)

async def set_caption_command(client: Client, message: Message):
    """Handle /set_caption command"""
    user_id = message.from_user.id
    
    # Check if caption is provided
    if len(message.command) < 2:
        await message.reply_text(
            "**Set Custom Caption**\n\n"
            "**Usage:** `/set_caption Your caption here`\n\n"
            "**Available variables:**\n"
            "`{file_name}` - File name\n"
            "`{file_size}` - File size\n\n"
            "**Example:**\n"
            "`/set_caption {file_name}\n{file_size}\n@mychannel`"
        )
        return
    
    # Get caption (everything after /set_caption)
    caption = message.text.split(None, 1)[1]
    
    # Save to database
    await db.set_caption(user_id, caption)
    
    await message.reply_text(
        f"✅ **Caption saved successfully!**\n\n"
        f"**Your caption:**\n{caption}\n\n"
        f"This will be used for all your processed videos."
    )

async def see_caption_command(client: Client, message: Message):
    """Handle /see_caption command"""
    user_id = message.from_user.id
    
    caption = await db.get_caption(user_id)
    
    if not caption:
        await message.reply_text(
            "❌ **No caption set**\n\n"
            "Use /set_caption to set a custom caption."
        )
        return
    
    await message.reply_text(
        f"**Your current caption:**\n\n{caption}"
    )

async def del_caption_command(client: Client, message: Message):
    """Handle /del_caption command"""
    user_id = message.from_user.id
    
    await db.set_caption(user_id, None)
    
    await message.reply_text("✅ Caption deleted successfully!")

async def view_thumb_command(client: Client, message: Message):
    """Handle /view_thumb command"""
    user_id = message.from_user.id
    
    thumb_file_id = await db.get_thumbnail(user_id)
    
    if not thumb_file_id:
        await message.reply_text(
            "❌ **No thumbnail set**\n\n"
            "Send me a photo to set as your custom thumbnail."
        )
        return
    
    try:
        await message.reply_photo(
            photo=thumb_file_id,
            caption="**Your current thumbnail**\n\nSend a new photo to update it."
        )
    except Exception as e:
        logger.error(f"Error sending thumbnail: {e}")
        await message.reply_text("❌ Error retrieving thumbnail. Please set a new one.")

async def del_thumb_command(client: Client, message: Message):
    """Handle /del_thumb command"""
    user_id = message.from_user.id
    
    await db.set_thumbnail(user_id, None)
    
    # Delete local thumbnail file if exists
    thumb_path = THUMB_DIR / f"{user_id}.jpg"
    if thumb_path.exists():
        thumb_path.unlink()
    
    await message.reply_text("✅ Thumbnail deleted successfully!")

async def users_command(client: Client, message: Message):
    """Handle /users command (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    total = await db.total_users_count()
    
    await message.reply_text(f"👥 **Total Users:** `{total}`")

async def ban_command(client: Client, message: Message):
    """Handle /ban command (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    # Check if user ID is provided
    if len(message.command) < 2:
        await message.reply_text(
            "**Ban User**\n\n"
            "**Usage:** `/ban user_id [reason]`\n\n"
            "**Example:** `/ban 123456789 Spamming`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        await db.ban_user(user_id, reason)
        
        await message.reply_text(
            f"✅ **User banned successfully!**\n\n"
            f"**User ID:** `{user_id}`\n"
            f"**Reason:** {reason}"
        )
        
        # Try to notify the user
        try:
            await client.send_message(
                user_id,
                f"🚫 **You have been banned from using this bot**\n\n"
                f"**Reason:** {reason}\n\n"
                f"Contact the bot admin if you think this is a mistake."
            )
        except:
            pass
            
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric ID.")
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

async def unban_command(client: Client, message: Message):
    """Handle /unban command (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    # Check if user ID is provided
    if len(message.command) < 2:
        await message.reply_text(
            "**Unban User**\n\n"
            "**Usage:** `/unban user_id`\n\n"
            "**Example:** `/unban 123456789`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        
        await db.remove_ban(user_id)
        
        await message.reply_text(
            f"✅ **User unbanned successfully!**\n\n"
            f"**User ID:** `{user_id}`"
        )
        
        # Try to notify the user
        try:
            await client.send_message(
                user_id,
                "✅ **You have been unbanned!**\n\n"
                "You can now use the bot again."
            )
        except:
            pass
            
    except ValueError:
        await message.reply_text("❌ Invalid user ID. Please provide a valid numeric ID.")
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

async def broadcast_command(client: Client, message: Message):
    """Handle /broadcast command (admin only)"""
    if not is_admin(message.from_user.id):
        return
    
    if not message.reply_to_message:
        await message.reply_text(
            "**Broadcast Message**\n\n"
            "Reply to a message with /broadcast to send it to all users."
        )
        return
    
    users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    total = 0
    successful = 0
    failed = 0
    
    status_msg = await message.reply_text("📢 Broadcasting message...")
    
    async for user in users:
        total += 1
        try:
            await broadcast_msg.copy(user['_id'])
            successful += 1
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {user['_id']}: {e}")
    
    await status_msg.edit_text(
        f"✅ **Broadcast completed!**\n\n"
        f"**Total users:** {total}\n"
        f"**Successful:** {successful}\n"
        f"**Failed:** {failed}"
    )
