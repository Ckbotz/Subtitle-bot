#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_subtitle_format(subtitle_file):
    """Detect subtitle format from file extension"""
    ext = Path(subtitle_file).suffix.lower()
    formats = {
        '.srt': 'srt',
        '.ass': 'ass',
        '.ssa': 'ass',
        '.vtt': 'webvtt',
        '.sub': 'subrip'
    }
    return formats.get(ext, 'srt')

def embed_multiple_subtitles(video_file, subtitle_files, output_file=None, languages=None, titles=None):
    """
    Embed multiple subtitle tracks into a video file
    Preserves all original streams except subtitles
    
    Args:
        video_file: Path to input video file
        subtitle_files: List of subtitle file paths
        output_file: Path to output video file (optional)
        languages: List of language codes (optional)
        titles: List of subtitle titles (optional)
    """
    
    if not os.path.exists(video_file):
        logger.error(f"Video file '{video_file}' not found")
        return False
    
    # Validate all subtitle files
    for sub_file in subtitle_files:
        if not os.path.exists(sub_file):
            logger.error(f"Subtitle file '{sub_file}' not found")
            return False
    
    # Generate output filename if not provided
    if output_file is None:
        video_path = Path(video_file)
        output_file = video_path.parent / f"{video_path.stem}_subbed{video_path.suffix}"
    
    # Detect video container format
    video_ext = Path(video_file).suffix.lower()
    is_mp4 = video_ext in ['.mp4', '.m4v']
    is_mkv = video_ext in ['.mkv', '.webm']
    
    # Build FFmpeg command
    cmd = ['ffmpeg', '-i', video_file]
    
    # Add all subtitle files as inputs
    for sub_file in subtitle_files:
        cmd.extend(['-i', sub_file])
    
    # Map all streams from the original video (video, audio, and other streams)
    cmd.extend(['-map', '0'])
    
    # Map all subtitle inputs
    for i in range(len(subtitle_files)):
        cmd.extend(['-map', str(i + 1)])
    
    # Copy all codecs from original file (video, audio, etc.)
    cmd.extend(['-c', 'copy'])
    
    # Set subtitle codec based on container format
    if is_mp4:
        # MP4 requires mov_text for subtitles
        cmd.extend(['-c:s', 'mov_text'])
    elif is_mkv:
        # MKV can handle various subtitle formats
        for i, sub_file in enumerate(subtitle_files):
            sub_format = get_subtitle_format(sub_file)
            if sub_format == 'ass':
                cmd.extend([f'-c:s:{i}', 'ass'])
            else:
                cmd.extend([f'-c:s:{i}', 'srt'])
    else:
        # For other formats, try to copy or use srt
        cmd.extend(['-c:s', 'srt'])
    
    # Add metadata for each subtitle
    for i, sub_file in enumerate(subtitle_files):
        lang = languages[i] if languages and i < len(languages) else 'und'
        cmd.extend([f'-metadata:s:s:{i}', f'language={lang}'])
        
        if titles and i < len(titles):
            cmd.extend([f'-metadata:s:s:{i}', f'title={titles[i]}'])
    
    # Add output file
    cmd.extend(['-y', str(output_file)])  # -y to overwrite without asking
    
    logger.info(f"Processing: {video_file}")
    logger.info(f"Adding {len(subtitle_files)} subtitle track(s)")
    logger.info(f"Output: {output_file}")
    logger.info(f"FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully created: {output_file}")
            return True
        else:
            logger.error(f"Error during processing:")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return False

def get_video_info(video_file):
    """
    Get information about the video file using ffprobe
    
    Args:
        video_file: Path to video file
    
    Returns:
        dict: Video information
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_file
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.error(f"Error getting video info: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting video info: {e}")
        return None
