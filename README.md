# 🎬 Telegram Subtitle Embedder Bot (Pyrogram)

A powerful Telegram bot that embeds soft subtitles into video files. Built with Pyrogram for better file handling and supports files up to 4GB!

## ✨ Features

- 📹 **Multiple Video Formats**: MP4, MKV, AVI, MOV, WebM, and more
- 📝 **Subtitle Formats**: SRT, ASS, SSA, VTT, SUB
- 🌍 **Multiple Languages**: Add multiple subtitle tracks in different languages
- 🎯 **Auto Language Detection**: Automatically detects language from filename
- 🖼️ **Thumbnail Preservation**: Keeps original video thumbnails
- 📦 **Stream Preservation**: Preserves all video, audio, and metadata streams
- 🚀 **Fast Processing**: No re-encoding, just stream copying
- 📈 **Progress Tracking**: Real-time upload/download progress
- 💪 **Large File Support**: Handles files up to 4GB (Pyrogram advantage!)
- 🌐 **Web Interface**: Health monitoring on port 8080

## 📋 Prerequisites

- Python 3.11+
- FFmpeg
- Telegram API ID and Hash (from [my.telegram.org/apps](https://my.telegram.org/apps))
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## 🔑 Getting API Credentials

### 1. Get API_ID and API_HASH

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Click on "API Development Tools"
4. Fill in the application details:
   - App title: Subtitle Bot
   - Short name: subtitlebot
   - Platform: Other
5. Copy your `api_id` and `api_hash`

### 2. Get BOT_TOKEN

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided

## 🚀 Quick Start

### Method 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telegram-subtitle-bot-pyrogram
```

2. **Create `.env` file**
```bash
cp .env.example .env
```

3. **Edit `.env` with your credentials**
```bash
nano .env
```

Add:
```env
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
```

4. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

5. **Check logs**
```bash
docker-compose logs -f
```

6. **Access web interface**
```
http://localhost:8080
```

### Method 2: Manual Installation

1. **Install FFmpeg**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export API_ID="12345678"
export API_HASH="your_api_hash_here"
export BOT_TOKEN="your_bot_token_here"
```

4. **Run the bot**
```bash
python main.py
```

## 📖 Usage

1. **Start the bot**
   - Send `/start` to your bot on Telegram

2. **Send video file**
   - Upload your video file to the bot
   - Bot shows progress during download

3. **Send subtitle files**
   - Upload one or more subtitle files
   - Bot will auto-detect language from filename (e.g., `movie.eng.srt`)
   - See progress for each subtitle download

4. **Process**
   - Send `/done` when all subtitles are uploaded
   - Wait for processing (usually takes a few seconds)
   - See upload progress
   - Receive your video with embedded subtitles!

## 🎯 Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message
- `/done` - Process video with uploaded subtitles
- `/cancel` - Cancel current operation

## 🌐 Web Interface

Access the web interface at `http://localhost:8080` to see:
- Bot status
- System metrics (CPU, Memory, Disk)
- Usage instructions
- Real-time statistics

### API Endpoints

- `GET /` - Main dashboard
- `GET /health` - Health check (JSON)
- `GET /status` - Detailed status (JSON)

## 📁 Project Structure

```
telegram-subtitle-bot-pyrogram/
├── main.py                 # Main entry point
├── bot.py                  # Pyrogram bot logic
├── subtitle_embedder.py    # FFmpeg subtitle embedding
├── web_server.py          # Flask web server
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🔧 Configuration

Edit `config.py` or set environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `API_ID` | Telegram API ID | Yes | - |
| `API_HASH` | Telegram API Hash | Yes | - |
| `BOT_TOKEN` | Telegram bot token | Yes | - |
| `PORT` | Web server port | No | 8080 |
| `HOST` | Web server host | No | 0.0.0.0 |
| `LOG_LEVEL` | Logging level | No | INFO |

## 🐳 Docker Commands

**Build image:**
```bash
docker build -t subtitle-bot-pyrogram .
```

**Run container:**
```bash
docker run -d \
  -e API_ID="12345678" \
  -e API_HASH="your_api_hash" \
  -e BOT_TOKEN="your_token" \
  -p 8080:8080 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/sessions:/app/sessions \
  --name subtitle-bot \
  subtitle-bot-pyrogram
```

**View logs:**
```bash
docker logs -f subtitle-bot
```

**Stop container:**
```bash
docker stop subtitle-bot
```

**Restart container:**
```bash
docker restart subtitle-bot
```

## 🔍 Troubleshooting

### Bot not starting
- Check if all credentials are set correctly
- Verify API_ID is an integer (no quotes)
- Ensure BOT_TOKEN format is correct: `123456:ABC-DEF...`
- Check logs: `docker-compose logs -f`

### FFmpeg errors
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check if subtitle format is supported
- Verify video file is not corrupted

### Session errors
- Delete `sessions/` folder and restart
- Check file permissions

### Out of disk space
- Clean up downloads: `rm -rf downloads/* output/*`
- Check disk usage: `df -h`

### Upload/Download stuck
- Check internet connection
- Verify file size is under 4GB
- Restart the bot

## 📝 Supported Formats

### Video Formats
- MP4, MKV, AVI, MOV, FLV, WebM, WMV, M4V

### Subtitle Formats
- SRT (SubRip)
- ASS/SSA (Advanced SubStation Alpha)
- VTT (WebVTT)
- SUB (SubViewer)

### Language Detection
Bot auto-detects languages from filenames:
- `movie.eng.srt` → English (eng)
- `film.spa.srt` → Spanish (spa)
- `video.fr.srt` → French (fre)
- `show.de.srt` → German (ger)
- `anime.ja.srt` → Japanese (jpn)
- And many more...

## 🆚 Pyrogram vs python-telegram-bot

### Why Pyrogram?

✅ **Better file handling** - Up to 4GB files
✅ **Faster downloads** - More efficient chunking
✅ **Progress tracking** - Built-in progress callbacks
✅ **Better async** - True async/await support
✅ **More control** - Lower-level API access
✅ **Session management** - Persistent sessions

### Trade-offs

⚠️ Requires `api_id` and `api_hash`
⚠️ Slightly more complex setup

## 🛡️ Security

- Files are automatically cleaned up after processing
- Each user has isolated file storage
- Sessions are stored securely
- No sensitive data is logged
- All operations are user-isolated

## 🚀 Performance Tips

1. **Use SSD** for downloads/output folders
2. **Increase RAM** for large file processing
3. **Use Docker** for better resource management
4. **Monitor logs** for performance issues

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8080/health
```

### Status Check
```bash
curl http://localhost:8080/status
```

### Docker Stats
```bash
docker stats subtitle-bot
```

## 🔄 Updates

To update the bot:

```bash
# Pull latest changes
git pull

# Rebuild Docker image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📜 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Open an issue on GitHub

## 🙏 Credits

- Built with [Pyrogram](https://docs.pyrogram.org/)
- Powered by [FFmpeg](https://ffmpeg.org/)
- Web server with [Flask](https://flask.palletsprojects.com/)

## 📞 Contact

- Telegram: [@YourBot](https://t.me/YourBot)
- Issues: GitHub Issues

---

**Made with ❤️ for the Telegram community! 🎬✨**

**Enjoy embedding subtitles with Pyrogram! 🚀**
