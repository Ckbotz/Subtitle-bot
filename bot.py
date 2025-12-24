#!/usr/bin/env python3
"""
Telegram Subtitle Embedder Bot - Pyrogram Version
Main bot file with database integration
"""

import os
import logging
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pathlib import Path
import asyncio
from subtitle_embedder import embed_multiple_subtitles
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR, OUTPUT_DIR, THUMB_DIR
from database import db
from utils import check_user_ban, format_caption
import commands

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
app = Client(
    "subtitle_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="."
)

# User session data structure
user_sessions = {}

# Track last update time for progress callbacks
progress_trackers = {}

class UserSession:
    def __init__(self):
        self.video_file = None
        self.video_path = None
        self.video_message = None
        self.video_is_document = False
        self.subtitle_files = []
        self.subtitle_paths = []
        self.subtitle_messages = []
        self.thumbnail = None
        self.thumbnail_path = None
        self.languages = []
        self.titles = []
        self.state = 'idle'
        self.file_name = None
        self.file_size = 0
        self.pending_language_selections = {}

# Language selection keyboard
def create_language_keyboard(subtitle_index):
    """Create inline keyboard for language selection"""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data=f"lang_{subtitle_index}_eng"),
            InlineKeyboardButton("🇪🇸 Spanish", callback_data=f"lang_{subtitle_index}_spa"),
            InlineKeyboardButton("🇫🇷 French", callback_data=f"lang_{subtitle_index}_fre")
        ],
        [
            InlineKeyboardButton("🇩🇪 German", callback_data=f"lang_{subtitle_index}_ger"),
            InlineKeyboardButton("🇮🇹 Italian", callback_data=f"lang_{subtitle_index}_ita"),
            InlineKeyboardButton("🇵🇹 Portuguese", callback_data=f"lang_{subtitle_index}_por")
        ],
        [
            InlineKeyboardButton("🇷🇺 Russian", callback_data=f"lang_{subtitle_index}_rus"),
            InlineKeyboardButton("🇯🇵 Japanese", callback_data=f"lang_{subtitle_index}_jpn"),
            InlineKeyboardButton("🇰🇷 Korean", callback_data=f"lang_{subtitle_index}_kor")
        ],
        [
            InlineKeyboardButton("🇨🇳 Chinese", callback_data=f"lang_{subtitle_index}_chi"),
            InlineKeyboardButton("🇮🇳 Hindi", callback_data=f"lang_{subtitle_index}_hin"),
            InlineKeyboardButton("🇸🇦 Arabic", callback_data=f"lang_{subtitle_index}_ara")
        ],
        [
            InlineKeyboardButton("❓ Unknown", callback_data=f"lang_{subtitle_index}_und")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Middleware to check if user is banned
@app.on_message(filters.private, group=-1)
async def check_ban(client: Client, message: Message):
    """Check if user is banned before processing any message"""
    user_id = message.from_user.id
    
    is_banned, ban_reason = await check_user_ban(db, user_id)
    
    if is_banned:
        await message.reply_text(
            f"🚫 **You are banned from using this bot**\n\n"
            f"**Reason:** {ban_reason}\n\n"
            f"Contact the bot admin if you think this is a mistake."
        )
        raise StopPropagation

@app.on_callback_query(filters.regex(r"^lang_"))
async def language_callback(client: Client, callback_query: CallbackQuery):
    """Handle language selection callback"""
    user_id = callback_query.from_user.id
    
    if user_id not in user_sessions:
        await callback_query.answer("❌ Session expired. Please start again.", show_alert=True)
        return
    
    session = user_sessions[user_id]
    
    # Parse callback data: lang_index_code
    parts = callback_query.data.split('_')
    subtitle_index = int(parts[1])
    language_code = parts[2]
    
    # Update language for this subtitle
    if subtitle_index < len(session.languages):
        session.languages[subtitle_index] = language_code
        
        # Language name mapping
        lang_names = {
            'eng': '🇬🇧 English',
            'spa': '🇪🇸 Spanish',
            'fre': '🇫🇷 French',
            'ger': '🇩🇪 German',
            'ita': '🇮🇹 Italian',
            'por': '🇵🇹 Portuguese',
            'rus': '🇷🇺 Russian',
            'jpn': '🇯🇵 Japanese',
            'kor': '🇰🇷 Korean',
            'chi': '🇨🇳 Chinese',
            'hin': '🇮🇳 Hindi',
            'ara': '🇸🇦 Arabic',
            'und': '❓ Unknown'
        }
        
        lang_name = lang_names.get(language_code, language_code)
        
        # Update the message
        try:
            await callback_query.edit_message_text(
                f"✅ Subtitle {subtitle_index + 1} language set to: {lang_name}\n\n"
                f"Send more subtitles or /done to process."
            )
        except:
            pass
        
        await callback_query.answer(f"Language set to {lang_name}")
    else:
        await callback_query.answer("❌ Invalid subtitle index", show_alert=True)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    await commands.start_command(client, message)
    user_id = message.from_user.id
    user_sessions[user_id] = UserSession()

@app.on_message(filters.command("help"))
async def help_handler(client: Client, message: Message):
    """Handle /help command"""
    await commands.help_command(client, message)

@app.on_message(filters.command("set_caption"))
async def set_caption_handler(client: Client, message: Message):
    """Handle /set_caption command"""
    await commands.set_caption_command(client, message)

@app.on_message(filters.command("see_caption"))
async def see_caption_handler(client: Client, message: Message):
    """Handle /see_caption command"""
    await commands.see_caption_command(client, message)

@app.on_message(filters.command("del_caption"))
async def del_caption_handler(client: Client, message: Message):
    """Handle /del_caption command"""
    await commands.del_caption_command(client, message)

@app.on_message(filters.command("view_thumb"))
async def view_thumb_handler(client: Client, message: Message):
    """Handle /view_thumb command"""
    await commands.view_thumb_command(client, message)

@app.on_message(filters.command("del_thumb"))
async def del_thumb_handler(client: Client, message: Message):
    """Handle /del_thumb command"""
    await commands.del_thumb_command(client, message)

@app.on_message(filters.command("users"))
async def users_handler(client: Client, message: Message):
    """Handle /users command"""
    await commands.users_command(client, message)

@app.on_message(filters.command("ban"))
async def ban_handler(client: Client, message: Message):
    """Handle /ban command"""
    await commands.ban_command(client, message)

@app.on_message(filters.command("unban"))
async def unban_handler(client: Client, message: Message):
    """Handle /unban command"""
    await commands.unban_command(client, message)

@app.on_message(filters.command("broadcast"))
async def broadcast_handler(client: Client, message: Message):
    """Handle /broadcast command"""
    await commands.broadcast_command(client, message)

@app.on_message(filters.command("cancel"))
async def cancel_command(client: Client, message: Message):
    """Handle /cancel command"""
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        cleanup_user_files(user_id)
        user_sessions[user_id] = UserSession()
    
    await message.reply_text(
        "❌ Operation cancelled. Send a new video to start again."
    )

@app.on_message(filters.command("done"))
async def done_command(client: Client, message: Message):
    """Handle /done command - process the video"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        await message.reply_text("⚠️ Please send a video first!")
        return
    
    session = user_sessions[user_id]
    
    if session.state != 'waiting_for_subtitles':
        await message.reply_text("⚠️ Please send a video first!")
        return
    
    if not session.subtitle_paths:
        await message.reply_text("⚠️ Please send at least one subtitle file!")
        return
    
    # Process the video
    status_msg = await message.reply_text("⏳ Processing your video... This may take a few minutes.")
    
    try:
        # Create output file path
        video_path = Path(session.video_path)
        output_file = OUTPUT_DIR / f"{user_id}_{video_path.name}"
        
        # Embed subtitles
        success = embed_multiple_subtitles(
            str(session.video_path),
            session.subtitle_paths,
            str(output_file),
            session.languages if session.languages else None,
            session.titles if session.titles else None
        )
        
        if not success:
            await status_msg.edit_text("❌ Error processing video. Please try again.")
            cleanup_user_files(user_id)
            return
        
        # Send the processed video back
        await status_msg.edit_text("📤 Uploading processed video...")
        
        # Get file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        # Get custom caption or use default
        custom_caption = await db.get_caption(user_id)
        if custom_caption:
            caption = format_caption(custom_caption, session.file_name, file_size)
        else:
            caption = f"✅ **Processed Successfully!**\n\n"
            caption += f"📊 Subtitles: {len(session.subtitle_paths)} track(s) embedded\n"
            caption += f"📦 Size: {file_size_mb:.2f} MB\n"
            caption += f"🎬 File: `{session.file_name}`"
        
        # Get thumbnail - custom or default
        thumb = None
        custom_thumb_id = await db.get_thumbnail(user_id)
        
        if custom_thumb_id:
            # Download custom thumbnail
            thumb_path = THUMB_DIR / f"{user_id}.jpg"
            try:
                await client.download_media(custom_thumb_id, file_name=str(thumb_path))
                thumb = str(thumb_path)
            except Exception as e:
                logger.error(f"Error downloading custom thumbnail: {e}")
                # Fall back to video thumbnail
                if session.thumbnail_path and os.path.exists(session.thumbnail_path):
                    thumb = session.thumbnail_path
        elif session.thumbnail_path and os.path.exists(session.thumbnail_path):
            thumb = session.thumbnail_path
        
        # Initialize progress tracker for upload
        tracker_key = f"{user_id}_upload"
        progress_trackers[tracker_key] = time.time()
        
        # Send video based on how it was received
        if session.video_is_document:
            await client.send_document(
                chat_id=message.chat.id,
                document=str(output_file),
                caption=caption,
                thumb=thumb,
                file_name=session.file_name,
                progress=progress_callback,
                progress_args=(status_msg, "Uploading", tracker_key)
            )
        else:
            await client.send_video(
                chat_id=message.chat.id,
                video=str(output_file),
                caption=caption,
                thumb=thumb,
                supports_streaming=True,
                file_name=session.file_name,
                progress=progress_callback,
                progress_args=(status_msg, "Uploading", tracker_key)
            )
        
        # Clean up progress tracker
        if tracker_key in progress_trackers:
            del progress_trackers[tracker_key]
        
        await status_msg.delete()
        await message.reply_text("✅ Done! Send another video to process more files.")
        
    except Exception as e:
        logger.error(f"Error processing video for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Clean up
        cleanup_user_files(user_id)
        user_sessions[user_id] = UserSession()

@app.on_message(filters.photo)
async def handle_photo(client: Client, message: Message):
    """Handle photo uploads for thumbnail"""
    user_id = message.from_user.id
    
    try:
        # Get the largest photo
        photo = message.photo
        
        # Download photo
        thumb_path = THUMB_DIR / f"{user_id}.jpg"
        await message.download(file_name=str(thumb_path))
        
        # Save file_id to database
        await db.set_thumbnail(user_id, photo.file_id)
        
        await message.reply_text(
            "✅ **Thumbnail saved successfully!**\n\n"
            "This thumbnail will be used for all your processed videos.\n\n"
            "Use /view_thumb to see it or /del_thumb to delete it."
        )
        
    except Exception as e:
        logger.error(f"Error saving thumbnail for user {user_id}: {e}")
        await message.reply_text(f"❌ Error saving thumbnail: {str(e)}")

@app.on_message(filters.video)
async def handle_video(client: Client, message: Message):
    """Handle video file uploads"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    # Clean up any previous session
    cleanup_user_files(user_id)
    user_sessions[user_id] = UserSession()
    session = user_sessions[user_id]
    
    video = message.video
    
    status_msg = await message.reply_text("📥 Downloading video...")
    
    try:
        # Get filename
        file_name = video.file_name or f"video_{user_id}_{int(time.time())}.mp4"
        session.file_name = file_name
        session.file_size = video.file_size
        session.video_is_document = False
        
        # Download video with progress
        video_path = DOWNLOAD_DIR / f"{user_id}_{file_name}"
        
        # Initialize progress tracker
        tracker_key = f"{user_id}_video_download"
        progress_trackers[tracker_key] = time.time()
        
        await message.download(
            file_name=str(video_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading video", tracker_key)
        )
        
        # Clean up progress tracker
        if tracker_key in progress_trackers:
            del progress_trackers[tracker_key]
        
        session.video_message = message
        session.video_path = str(video_path)
        session.state = 'waiting_for_subtitles'
        
        # Handle thumbnail
        if video.thumbs:
            try:
                thumb_path = DOWNLOAD_DIR / f"{user_id}_thumb.jpg"
                await client.download_media(
                    message=video.thumbs[0].file_id,
                    file_name=str(thumb_path)
                )
                session.thumbnail_path = str(thumb_path)
            except Exception as e:
                logger.warning(f"Could not download thumbnail: {e}")
        
        await status_msg.delete()
        
        file_size_mb = video.file_size / (1024 * 1024)
        await message.reply_text(
            f"✅ Video received!\n\n"
            f"📄 **Name:** `{file_name}`\n"
            f"📦 **Size:** {file_size_mb:.2f} MB\n"
            f"⏱ **Duration:** {format_duration(video.duration)}\n\n"
            f"Now send your subtitle file(s).\n"
            f"You can send multiple subtitle files for different languages.\n"
            f"When done, send /done to process."
        )
        
    except Exception as e:
        logger.error(f"Error downloading video for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error downloading video: {str(e)}")

@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    """Handle document uploads (subtitles or videos)"""
    user_id = message.from_user.id
    document = message.document
    
    if not document.file_name:
        await message.reply_text("⚠️ Invalid file!")
        return
    
    file_ext = Path(document.file_name).suffix.lower()
    
    # Check if it's a video file
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v']
    if file_ext in video_extensions:
        await handle_video_document(client, message)
        return
    
    # Check if it's a subtitle file
    subtitle_extensions = ['.srt', '.ass', '.ssa', '.vtt', '.sub']
    if file_ext not in subtitle_extensions:
        await message.reply_text(
            "⚠️ Unsupported file format.\n"
            "Supported subtitle formats: SRT, ASS, SSA, VTT, SUB"
        )
        return
    
    if user_id not in user_sessions or user_sessions[user_id].state != 'waiting_for_subtitles':
        await message.reply_text("⚠️ Please send a video file first!")
        return
    
    session = user_sessions[user_id]
    
    status_msg = await message.reply_text(f"📥 Downloading subtitle {len(session.subtitle_paths) + 1}...")
    
    try:
        # Download subtitle
        subtitle_path = DOWNLOAD_DIR / f"{user_id}_sub_{len(session.subtitle_paths)}_{document.file_name}"
        
        # Initialize progress tracker
        tracker_key = f"{user_id}_subtitle_{len(session.subtitle_paths)}_download"
        progress_trackers[tracker_key] = time.time()
        
        await message.download(
            file_name=str(subtitle_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading subtitle", tracker_key)
        )
        
        # Clean up progress tracker
        if tracker_key in progress_trackers:
            del progress_trackers[tracker_key]
        
        subtitle_index = len(session.subtitle_paths)
        
        session.subtitle_files.append(document)
        session.subtitle_paths.append(str(subtitle_path))
        session.subtitle_messages.append(message.id)
        
        # Initialize with 'und' language
        session.languages.append('und')
        session.titles.append(document.file_name.rsplit('.', 1)[0])
        
        await status_msg.delete()
        
        file_size_kb = document.file_size / 1024
        
        # Send language selection keyboard
        lang_msg = await message.reply_text(
            f"✅ Subtitle {len(session.subtitle_paths)} received!\n\n"
            f"📄 **Name:** `{document.file_name}`\n"
            f"📦 **Size:** {file_size_kb:.2f} KB\n\n"
            f"🌍 **Please select the language for this subtitle:**",
            reply_markup=create_language_keyboard(subtitle_index)
        )
        
        session.pending_language_selections[subtitle_index] = lang_msg.id
        
    except Exception as e:
        logger.error(f"Error downloading subtitle for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error downloading subtitle: {str(e)}")

async def handle_video_document(client: Client, message: Message):
    """Handle video files sent as documents"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    
    # Clean up any previous session
    cleanup_user_files(user_id)
    user_sessions[user_id] = UserSession()
    session = user_sessions[user_id]
    
    document = message.document
    
    status_msg = await message.reply_text("📥 Downloading video...")
    
    try:
        # Get filename
        file_name = document.file_name
        session.file_name = file_name
        session.file_size = document.file_size
        session.video_is_document = True
        
        # Download video with progress
        video_path = DOWNLOAD_DIR / f"{user_id}_{file_name}"
        
        # Initialize progress tracker
        tracker_key = f"{user_id}_video_document_download"
        progress_trackers[tracker_key] = time.time()
        
        await message.download(
            file_name=str(video_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading video", tracker_key)
        )
        
        # Clean up progress tracker
        if tracker_key in progress_trackers:
            del progress_trackers[tracker_key]
        
        session.video_message = message
        session.video_path = str(video_path)
        session.state = 'waiting_for_subtitles'
        
        await status_msg.delete()
        
        file_size_mb = document.file_size / (1024 * 1024)
        await message.reply_text(
            f"✅ Video received!\n\n"
            f"📄 **Name:** `{file_name}`\n"
            f"📦 **Size:** {file_size_mb:.2f} MB\n\n"
            f"Now send your subtitle file(s).\n"
            f"You can send multiple subtitle files for different languages.\n"
            f"When done, send /done to process."
        )
        
    except Exception as e:
        logger.error(f"Error downloading video for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error downloading video: {str(e)}")

async def progress_callback(current, total, status_msg, action="Processing", tracker_key=None):
    """Progress callback for downloads/uploads with 10 second interval"""
    try:
        current_time = time.time()
        
        # Get the last update time for this specific operation
        if tracker_key is None:
            tracker_key = "default"
        
        last_update_time = progress_trackers.get(tracker_key, 0)
        
        # Update only every 10 seconds
        if (current_time - last_update_time) >= 10:
            percentage = (current / total) * 100
            progress_bar = create_progress_bar(percentage)
            text = f"{action}... {percentage:.1f}%\n{progress_bar}\n{format_bytes(current)} / {format_bytes(total)}"
            
            try:
                await status_msg.edit_text(text)
                progress_trackers[tracker_key] = current_time
            except Exception as e:
                logger.debug(f"Could not edit message: {e}")
                pass
    except Exception as e:
        logger.debug(f"Progress callback error: {e}")

def create_progress_bar(percentage, length=20):
    """Create a text progress bar"""
    filled = int(length * percentage / 100)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}]"

def format_bytes(size):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def format_duration(seconds):
    """Format duration in seconds to readable format"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def cleanup_user_files(user_id):
    """Clean up all files for a user"""
    try:
        for file_path in DOWNLOAD_DIR.glob(f"{user_id}_*"):
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"Deleted: {file_path}")
        
        for file_path in OUTPUT_DIR.glob(f"{user_id}_*"):
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"Deleted: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up files for user {user_id}: {e}")

def run_bot():
    """Run the bot"""
    # Create necessary directories
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    THUMB_DIR.mkdir(exist_ok=True)
    
    logger.info("Starting Pyrogram bot with database integration...")
    app.run()

if __name__ == '__main__':
    run_bot()
