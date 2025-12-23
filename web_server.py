#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
import logging
from config import WEB_SERVER_PORT, WEB_SERVER_HOST
import psutil
import os
from pathlib import Path

app = Flask(__name__)
logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Subtitle Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .status-label {
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }
        .healthy {
            color: #4ade80;
        }
        .info {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .info h2 {
            margin-top: 0;
        }
        .info ul {
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Telegram Subtitle Bot</h1>
        
        <div class="status">
            <span class="status-label">Status:</span>
            <span class="healthy">✓ Online and Running</span>
        </div>
        
        <div class="status">
            <span class="status-label">CPU Usage:</span>
            <span>{{ cpu_percent }}%</span>
        </div>
        
        <div class="status">
            <span class="status-label">Memory Usage:</span>
            <span>{{ memory_percent }}%</span>
        </div>
        
        <div class="status">
            <span class="status-label">Disk Usage:</span>
            <span>{{ disk_percent }}%</span>
        </div>
        
        <div class="info">
            <h2>📖 How to Use</h2>
            <ul>
                <li>Search for the bot on Telegram</li>
                <li>Send /start to begin</li>
                <li>Send a video file</li>
                <li>Send subtitle file(s)</li>
                <li>Send /done to process</li>
                <li>Receive your video with embedded subtitles!</li>
            </ul>
        </div>
        
        <div class="info">
            <h2>✨ Features</h2>
            <ul>
                <li>Supports multiple subtitle formats (SRT, ASS, VTT, etc.)</li>
                <li>Multiple subtitle tracks support</li>
                <li>Preserves original video quality</li>
                <li>Preserves thumbnails</li>
                <li>Auto-detects subtitle language</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return render_template_string(
            HTML_TEMPLATE,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent
        )
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return render_template_string(HTML_TEMPLATE, 
                                     cpu_percent=0, 
                                     memory_percent=0, 
                                     disk_percent=0)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/status')
def status():
    """Detailed status endpoint"""
    try:
        from config import DOWNLOAD_DIR, OUTPUT_DIR
        
        # Count files in directories
        download_files = len(list(DOWNLOAD_DIR.glob('*'))) if DOWNLOAD_DIR.exists() else 0
        output_files = len(list(OUTPUT_DIR.glob('*'))) if OUTPUT_DIR.exists() else 0
        
        return jsonify({
            'status': 'running',
            'bot': {
                'active': True,
                'version': '1.0.0'
            },
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            },
            'files': {
                'download_dir': download_files,
                'output_dir': output_files
            }
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def run_server():
    """Run the Flask web server"""
    logger.info(f"Starting web server on {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
    app.run(host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, debug=False)

if __name__ == '__main__':
    run_server()
