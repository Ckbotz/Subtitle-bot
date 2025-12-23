#!/usr/bin/env python3
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pathlib import Path
import asyncio
from subtitle_embedder import embed_multiple_subtitles
from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR, OUTPUT_DIR

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

class UserSession:
    def __init__(self):
        self.video_file = None
        self.video_path = None
        self.video_message = None
        self.subtitle_files = []
        self.subtitle_paths = []
        self.thumbnail = None
        self.thumbnail_path = None
        self.languages = []
        self.titles = []
        self.state = 'idle'  # idle, waiting_for_video, waiting_for_subtitles
        self.file_name = None

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    user_sessions[user_id] = UserSession()
    
    welcome_message = """
🎬 **Subtitle Embedder Bot**

Welcome! I can embed subtitles into your video files.

**How to use:**
1. Send me a video file
2. Send subtitle file(s) - you can send multiple
3. Send /done when you've sent all subtitles
4. I'll process and send back your video with embedded subtitles

**Supported formats:**
📹 Video: MP4, MKV, AVI, MOV, etc.
📝 Subtitles: SRT, ASS, SSA, VTT, SUB

**Commands:**
/start - Start the bot
/cancel - Cancel current operation
/help - Show this message

**Features:**
✨ Supports files up to 4GB
✨ Multiple subtitle tracks
✨ Preserves video quality
✨ Keeps original thumbnail
✨ Auto-detects language
"""
    await message.reply_text(welcome_message)

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    await start_command(client, message)

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
        
        # Get original file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        caption = f"✅ **Processed Successfully!**\n\n"
        caption += f"📊 Subtitles: {len(session.subtitle_paths)} track(s) embedded\n"
        caption += f"📦 Size: {file_size_mb:.2f} MB\n"
        caption += f"🎬 File: `{session.file_name}`"
        
        # Send with thumbnail if available
        thumb = session.thumbnail_path if session.thumbnail_path and os.path.exists(session.thumbnail_path) else None
        
        # Send video with progress
        await client.send_video(
            chat_id=message.chat.id,
            video=str(output_file),
            caption=caption,
            thumb=thumb,
            supports_streaming=True,
            file_name=session.file_name,
            progress=progress_callback,
            progress_args=(status_msg, "Uploading")
        )
        
        await status_msg.delete()
        await message.reply_text("✅ Done! Send another video to process more files.")
        
    except Exception as e:
        logger.error(f"Error processing video for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        # Clean up
        cleanup_user_files(user_id)
        user_sessions[user_id] = UserSession()

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
        file_name = video.file_name or f"video_{user_id}.mp4"
        session.file_name = file_name
        
        # Download video with progress
        video_path = DOWNLOAD_DIR / f"{user_id}_{file_name}"
        
        await message.download(
            file_name=str(video_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading video")
        )
        
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
        
        await message.download(
            file_name=str(subtitle_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading subtitle")
        )
        
        session.subtitle_files.append(document)
        session.subtitle_paths.append(str(subtitle_path))
        
        # Try to extract language from filename
        filename_lower = document.file_name.lower()
        language = extract_language_from_filename(filename_lower)
        session.languages.append(language)
        session.titles.append(document.file_name.rsplit('.', 1)[0])
        
        await status_msg.delete()
        
        file_size_kb = document.file_size / 1024
        await message.reply_text(
            f"✅ Subtitle {len(session.subtitle_paths)} received!\n\n"
            f"📄 **Name:** `{document.file_name}`\n"
            f"📦 **Size:** {file_size_kb:.2f} KB\n"
            f"🌍 **Language:** {language}\n\n"
            f"Send more subtitles or /done to process."
        )
        
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
        
        # Download video with progress
        video_path = DOWNLOAD_DIR / f"{user_id}_{file_name}"
        
        await message.download(
            file_name=str(video_path),
            progress=progress_callback,
            progress_args=(status_msg, "Downloading video")
        )
        
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

async def progress_callback(current, total, status_msg, action="Processing"):
    """Progress callback for downloads/uploads"""
    try:
        percentage = (current / total) * 100
        
        # Update every 5%
        if int(percentage) % 5 == 0:
            progress_bar = create_progress_bar(percentage)
            text = f"{action}... {percentage:.1f}%\n{progress_bar}\n{format_bytes(current)} / {format_bytes(total)}"
            
            try:
                await status_msg.edit_text(text)
            except:
                pass  # Ignore FloodWait and other errors
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

def extract_language_from_filename(filename):
    """Extract language code from filename"""
    language_codes = {
        'eng': 'eng', 'en': 'eng', 'english': 'eng',
        'spa': 'spa', 'es': 'spa', 'spanish': 'spa',
        'fre': 'fre', 'fr': 'fre', 'french': 'fre',
        'ger': 'ger', 'de': 'ger', 'german': 'ger',
        'ita': 'ita', 'it': 'ita', 'italian': 'ita',
        'por': 'por', 'pt': 'por', 'portuguese': 'por',
        'rus': 'rus', 'ru': 'rus', 'russian': 'rus',
        'jpn': 'jpn', 'ja': 'jpn', 'japanese': 'jpn',
        'kor': 'kor', 'ko': 'kor', 'korean': 'kor',
        'chi': 'chi', 'zh': 'chi', 'chinese': 'chi',
        'ara': 'ara', 'ar': 'ara', 'arabic': 'ara',
        'hin': 'hin', 'hi': 'hin', 'hindi': 'hin',
    }
    
    for code, standard in language_codes.items():
        if code in filename:
            return standard
    
    return 'und'  # undefined

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
    
    logger.info("Starting Pyrogram bot...")
    app.run()

if __name__ == '__main__':
    run_bot()
