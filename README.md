# 🎬 Telegram Subtitle Embedder Bot

A powerful Telegram bot that embeds subtitle files into video files with support for multiple subtitle tracks, custom thumbnails, and captions. Built with Pyrogram and MongoDB.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green.svg)](https://docs.pyrogram.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.0+-brightgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### Core Functionality
- 📹 **Video Processing**: Supports MP4, MKV, AVI, MOV, WebM, and more
- 📝 **Subtitle Formats**: SRT, ASS, SSA, VTT, SUB
- 🌍 **Multiple Subtitle Tracks**: Add multiple subtitle files in different languages
- 🎯 **Language Selection**: Interactive language picker for each subtitle
- 🚀 **Fast Processing**: No re-encoding, preserves original video and audio quality
- 📦 **Large File Support**: Handles files up to 4GB (Telegram limit)

### Customization Features
- 🖼️ **Custom Thumbnails**: Set your own thumbnail for processed videos
- 📋 **Custom Captions**: Create caption templates with variables
- 🎨 **Caption Variables**: `{file_name}` and `{file_size}` support
- 💾 **User Preferences**: Thumbnails and captions saved per user

### Admin Features
- 👥 **User Management**: View total user count
- 🚫 **Ban/Unban System**: Block abusive users
- 📢 **Broadcast Messages**: Send announcements to all users
- 📊 **User Tracking**: MongoDB-based user database
- 📝 **Activity Logs**: Optional log channel for new user tracking

### Technical Features
- ⚡ **Asynchronous Processing**: Non-blocking operations
- 🔄 **Progress Tracking**: Real-time upload/download progress
- 🛡️ **Error Handling**: Comprehensive error management
- 🐳 **Docker Support**: Easy deployment with Docker
- 🌐 **Web Server**: Health check endpoint included

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Prerequisites

### Required Software
- Python 3.8 or higher
- MongoDB 4.0 or higher
- FFmpeg (for video processing)
- FFprobe (usually comes with FFmpeg)

### Telegram Requirements
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- API ID and API Hash from [my.telegram.org](https://my.telegram.org)

### System Requirements
- **RAM**: Minimum 512MB, Recommended 2GB+
- **Storage**: Depends on usage (temporary files are cleaned automatically)
- **CPU**: Multi-core recommended for faster processing

## 📥 Installation

### Method 1: Standard Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/subtitle-embedder-bot.git
cd subtitle-embedder-bot
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install FFmpeg**

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
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

5. **Install and start MongoDB**

**Ubuntu/Debian:**
```bash
sudo apt install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
Download from [mongodb.com](https://www.mongodb.com/try/download/community)

6. **Configure environment variables**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

7. **Run the bot**
```bash
python bot.py
```

### Method 2: Docker Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/subtitle-embedder-bot.git
cd subtitle-embedder-bot
```

2. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

3. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

4. **View logs**
```bash
docker-compose logs -f bot
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Telegram API Configuration
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# MongoDB Configuration
DB_URL=mongodb://localhost:27017
DB_NAME=subtitle_bot

# Admin Configuration (comma-separated user IDs)
ADMINS=123456789,987654321

# Optional: Log Channel (for new user notifications)
LOG_CHANNEL=-1001234567890

# Web Server Configuration
PORT=8080
HOST=0.0.0.0

# FFmpeg Configuration (optional)
FFMPEG_PATH=ffmpeg

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### Getting Your Credentials

#### 1. Bot Token
- Open Telegram and search for [@BotFather](https://t.me/botfather)
- Send `/newbot` and follow the instructions
- Copy the token provided

#### 2. API ID and API Hash
- Go to [my.telegram.org](https://my.telegram.org)
- Log in with your phone number
- Go to "API Development Tools"
- Create a new application
- Copy the `api_id` and `api_hash`

#### 3. Admin IDs
- Send a message to [@userinfobot](https://t.me/userinfobot)
- Copy your user ID
- For multiple admins, separate IDs with commas: `123456789,987654321`

#### 4. Log Channel (Optional)
- Create a channel or group
- Add your bot as admin
- Get the channel ID using [@username_to_id_bot](https://t.me/username_to_id_bot)
- Channel IDs start with `-100`

## 📱 Usage

### Basic Workflow

1. **Start the bot**
```
/start
```

2. **Send a video file**
   - Send as video or document
   - Supports up to 4GB files

3. **Send subtitle file(s)**
   - Send one or more subtitle files
   - Select language for each subtitle
   - Supported formats: SRT, ASS, SSA, VTT, SUB

4. **Process the video**
```
/done
```

5. **Receive processed video**
   - Bot will embed subtitles
   - Preserves video and audio quality
   - Applies your custom thumbnail/caption if set

### Setting Custom Thumbnail

1. **Send a photo to the bot**
   - Any photo you want as thumbnail
   - Bot will save it automatically

2. **View your thumbnail**
```
/view_thumb
```

3. **Delete thumbnail**
```
/del_thumb
```

### Setting Custom Caption

1. **Set caption with variables**
```
/set_caption 📁 {file_name}
📦 Size: {file_size}
✅ Processed by @YourBot
```

2. **View current caption**
```
/see_caption
```

3. **Delete caption**
```
/del_caption
```

**Available Variables:**
- `{file_name}` - Name of the video file
- `{file_size}` - Size of the file (e.g., "150.25 MB")

## 🤖 Commands

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and register |
| `/help` | Show help message |
| `/cancel` | Cancel current operation |
| `/done` | Process video with subtitles |
| `/set_caption <text>` | Set custom caption template |
| `/see_caption` | View your current caption |
| `/del_caption` | Delete custom caption |
| `/view_thumb` | View your thumbnail |
| `/del_thumb` | Delete your thumbnail |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/users` | Get total user count |
| `/ban <user_id> [reason]` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/broadcast` | Broadcast message (reply to a message) |

### Command Examples

**Set custom caption:**
```
/set_caption 🎬 {file_name}
📦 {file_size}
✨ Subtitles by @MyChannel
```

**Ban a user:**
```
/ban 123456789 Spamming
```

**Unban a user:**
```
/unban 123456789
```

**Broadcast:**
Reply to any message with `/broadcast` to send it to all users

## 📁 Project Structure

```
subtitle-embedder-bot/
├── bot.py                  # Main bot file with message handlers
├── commands.py             # Command handlers (admin, caption, thumbnail)
├── config.py              # Configuration and environment variables
├── database.py            # MongoDB database operations
├── subtitle_embedder.py   # FFmpeg subtitle embedding logic
├── utils.py               # Helper utilities (logging, formatting)
├── web_server.py          # Health check web server (optional)
├── main.py                # Entry point (runs bot + web server)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── LICENSE              # License file
└── README.md            # This file

# Auto-generated directories
├── downloads/           # Temporary video/subtitle downloads
├── output/             # Processed videos (temporary)
├── thumbnails/         # User custom thumbnails
└── sessions/           # Pyrogram session files
```

### File Descriptions

#### Core Files

**bot.py**
- Main bot logic and message handlers
- Video and subtitle upload handlers
- Language selection system
- Progress tracking for uploads/downloads
- Session management

**commands.py**
- User command handlers (`/start`, `/help`, `/set_caption`, etc.)
- Admin command handlers (`/ban`, `/unban`, `/users`, `/broadcast`)
- Thumbnail management commands
- Caption management commands

**config.py**
- Environment variable loading
- Directory configuration
- File size limits
- Bot settings and constants
- Config class for easy access

**database.py**
- MongoDB connection and operations
- User registration and management
- Ban/unban operations
- Thumbnail and caption storage
- User preference management

**subtitle_embedder.py**
- FFmpeg wrapper for subtitle embedding
- Video stream management
- Subtitle format detection
- Container format handling (MP4, MKV, etc.)
- Video information extraction

**utils.py**
- Logging utilities
- User ban checking
- Caption formatting with variables
- Admin verification
- Helper functions

#### Optional Files

**web_server.py**
- Flask/Aiohttp web server
- Health check endpoint
- Useful for monitoring and uptime checks

**main.py**
- Combined entry point
- Runs bot and web server together
- Useful for platforms like Heroku, Railway

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: subtitle_bot_mongo
    restart: unless-stopped
    volumes:
      - mongodb_data:/data/db
    networks:
      - bot_network

  bot:
    build: .
    container_name: subtitle_bot
    restart: unless-stopped
    depends_on:
      - mongodb
    env_file:
      - .env
    environment:
      - DB_URL=mongodb://mongodb:27017
    volumes:
      - ./downloads:/app/downloads
      - ./output:/app/output
      - ./thumbnails:/app/thumbnails
      - ./sessions:/app/sessions
    networks:
      - bot_network
    ports:
      - "8080:8080"

volumes:
  mongodb_data:

networks:
  bot_network:
```

**Commands:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down

# Restart bot
docker-compose restart bot

# Update bot
git pull
docker-compose build
docker-compose up -d
```

### Using Dockerfile Only

**Build image:**
```bash
docker build -t subtitle-bot .
```

**Run container:**
```bash
docker run -d \
  --name subtitle-bot \
  --env-file .env \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/thumbnails:/app/thumbnails \
  -v $(pwd)/sessions:/app/sessions \
  subtitle-bot
```

## 🔨 Development

### Setting Up Development Environment

1. **Install development dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If you have dev dependencies
```

2. **Enable debug logging**
```bash
export LOG_LEVEL=DEBUG
```

3. **Run with auto-reload**
```bash
# Install watchdog
pip install watchdog

# Run with auto-reload
watchmedo auto-restart -d . -p '*.py' -- python bot.py
```

### Code Style

This project follows PEP 8 guidelines. Format your code with:

```bash
# Install formatter
pip install black

# Format code
black .
```

### Testing

```bash
# Run tests (if available)
pytest

# With coverage
pytest --cov=.
```

### Adding New Features

1. **User commands** - Add to `commands.py`
2. **Admin commands** - Add to `commands.py` with admin check
3. **Database operations** - Add to `database.py`
4. **Video processing** - Modify `subtitle_embedder.py`
5. **Bot handlers** - Add to `bot.py`

## 🐛 Troubleshooting

### Common Issues

#### Bot doesn't start

**Problem:** `ModuleNotFoundError: No module named 'pyrogram'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

**Problem:** `MongoDB connection failed`

**Solution:**
```bash
# Check if MongoDB is running
sudo systemctl status mongodb

# Start MongoDB
sudo systemctl start mongodb

# Check connection
mongo --eval "db.stats()"
```

---

#### FFmpeg errors

**Problem:** `FFmpeg not found`

**Solution:**
```bash
# Install FFmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

---

**Problem:** `Subtitle embedding failed`

**Solution:**
1. Check FFmpeg is installed: `ffmpeg -version`
2. Check video file format compatibility
3. Check subtitle file encoding (should be UTF-8)
4. Check logs for detailed error: `docker-compose logs -f bot`

---

#### Permission errors

**Problem:** `Permission denied` when accessing files

**Solution:**
```bash
# Fix directory permissions
chmod -R 755 downloads output thumbnails sessions

# For Docker
sudo chown -R $USER:$USER downloads output thumbnails sessions
```

---

#### Database issues

**Problem:** Cannot connect to MongoDB

**Solution:**
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Check MongoDB logs
sudo journalctl -u mongodb -f

# Restart MongoDB
sudo systemctl restart mongodb
```

---

#### Large file upload fails

**Problem:** Timeout or memory error with large files

**Solution:**
1. Check available disk space: `df -h`
2. Check available RAM: `free -h`
3. Increase timeout in config
4. For Docker, increase memory limit in `docker-compose.yml`

---

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python bot.py
```

Or in `.env`:
```env
LOG_LEVEL=DEBUG
```

### Checking Logs

**Standard installation:**
```bash
# View bot output
python bot.py

# Or redirect to file
python bot.py > bot.log 2>&1
```

**Docker:**
```bash
# View live logs
docker-compose logs -f bot

# View last 100 lines
docker-compose logs --tail=100 bot

# Save logs to file
docker-compose logs bot > bot.log
```

### Database Inspection

**MongoDB Shell:**
```bash
# Connect to MongoDB
mongo

# Switch to bot database
use subtitle_bot

# View all users
db.users.find().pretty()

# Count users
db.users.count()

# Find specific user
db.users.findOne({_id: 123456789})

# Delete user
db.users.deleteOne({_id: 123456789})
```

## 📊 Performance Optimization

### For Production

1. **Use MongoDB indexes**
```javascript
// In MongoDB shell
db.users.createIndex({_id: 1})
db.users.createIndex({"ban_status.is_banned": 1})
```

2. **Enable MongoDB authentication**
```bash
# Create admin user in MongoDB
mongo admin --eval "db.createUser({user: 'admin', pwd: 'password', roles: ['root']})"

# Update DB_URL in .env
DB_URL=mongodb://admin:password@localhost:27017
```

3. **Use nginx reverse proxy** (for web server)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

4. **Set up automatic cleanup**
```bash
# Add to crontab
0 */6 * * * find /path/to/bot/downloads -type f -mtime +1 -delete
0 */6 * * * find /path/to/bot/output -type f -mtime +1 -delete
```

## 🚀 Deployment

### Deploy to VPS (Ubuntu/Debian)

1. **Install dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mongodb ffmpeg git
```

2. **Clone and setup**
```bash
git clone https://github.com/yourusername/subtitle-embedder-bot.git
cd subtitle-embedder-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
nano .env  # Add your credentials
```

4. **Setup as systemd service**

Create `/etc/systemd/system/subtitle-bot.service`:
```ini
[Unit]
Description=Subtitle Embedder Bot
After=network.target mongodb.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/subtitle-embedder-bot
Environment="PATH=/path/to/subtitle-embedder-bot/venv/bin"
ExecStart=/path/to/subtitle-embedder-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Start service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable subtitle-bot
sudo systemctl start subtitle-bot
sudo systemctl status subtitle-bot
```

### Deploy to Heroku

1. **Create Heroku app**
```bash
heroku create your-bot-name
```

2. **Add buildpacks**
```bash
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

3. **Add MongoDB addon**
```bash
heroku addons:create mongolab:sandbox
```

4. **Set config vars**
```bash
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMINS=your_user_id
```

5. **Deploy**
```bash
git push heroku main
```

### Deploy to Railway

1. **Create new project on Railway**
2. **Connect GitHub repository**
3. **Add MongoDB service**
4. **Set environment variables**
5. **Deploy automatically on push**

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**
4. **Commit your changes**
```bash
git commit -m "Add amazing feature"
```

5. **Push to branch**
```bash
git push origin feature/amazing-feature
```

6. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide
- Add comments to complex code
- Update documentation for new features
- Test your changes thoroughly
- Add error handling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Telegram: [@yourusername](https://t.me/yourusername)

## 🙏 Acknowledgments

- [Pyrogram](https://docs.pyrogram.org/) - Telegram Bot Framework
- [FFmpeg](https://ffmpeg.org/) - Video Processing
- [MongoDB](https://www.mongodb.com/) - Database
- [Motor](https://motor.readthedocs.io/) - Async MongoDB Driver

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/subtitle-embedder-bot/issues)
- **Telegram**: [@yoursupportgroup](https://t.me/yoursupportgroup)
- **Email**: support@yourdomain.com

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/subtitle-embedder-bot&type=Date)](https://star-history.com/#yourusername/subtitle-embedder-bot&Date)

---

**Made with ❤️ by @KichuTG**

*Last updated: December 24, 2025*
