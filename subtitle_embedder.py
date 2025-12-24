#!/usr/bin/env python3
"""
Subtitle Embedder - Complete Bot Compatible Version
Copies only video and audio streams, replaces original subtitles with new ones
Fixed output path handling
"""

import os
import subprocess
from pathlib import Path
import logging
import json
import shutil

logger = logging.getLogger(__name__)

def check_ffmpeg():
    """
    Check if FFmpeg is installed and available
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        subprocess.run(
            ['ffmpeg', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            timeout=5
        )
        logger.info("FFmpeg is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("FFmpeg is not installed or not available in PATH")
        return False

def check_ffprobe():
    """
    Check if FFprobe is installed and available
    
    Returns:
        bool: True if FFprobe is available, False otherwise
    """
    try:
        subprocess.run(
            ['ffprobe', '-version'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True,
            timeout=5
        )
        logger.info("FFprobe is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("FFprobe is not installed or not available in PATH")
        return False

def get_subtitle_format(subtitle_file):
    """
    Detect subtitle format from file extension
    
    Args:
        subtitle_file: Path to subtitle file
    
    Returns:
        str: Subtitle format identifier
    """
    ext = Path(subtitle_file).suffix.lower()
    formats = {
        '.srt': 'srt',
        '.ass': 'ass',
        '.ssa': 'ass',
        '.vtt': 'webvtt',
        '.sub': 'subrip'
    }
    return formats.get(ext, 'srt')

def ensure_output_directory(output_file):
    """
    Ensure the output directory exists
    
    Args:
        output_file: Path to output file
    
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        output_path = Path(output_file)
        output_dir = output_path.parent
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating output directory: {e}")
        return False

def get_video_info(video_file):
    """
    Get detailed information about the video file using ffprobe
    
    Args:
        video_file: Path to video file
    
    Returns:
        dict: Video information including streams, or None if error
    """
    if not os.path.exists(video_file):
        logger.error(f"Video file not found: {video_file}")
        return None
    
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
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            logger.error(f"FFprobe error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("FFprobe timeout while getting video info")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing FFprobe output: {e}")
        return None
    except Exception as e:
        logger.error(f"Exception getting video info: {e}")
        return None

def get_stream_count(video_file):
    """
    Get count of different stream types in video file
    
    Args:
        video_file: Path to video file
    
    Returns:
        dict: {'video': count, 'audio': count, 'subtitle': count} or None if error
    """
    info = get_video_info(video_file)
    if not info:
        return None
    
    counts = {'video': 0, 'audio': 0, 'subtitle': 0, 'data': 0}
    
    for stream in info.get('streams', []):
        codec_type = stream.get('codec_type', '').lower()
        if codec_type == 'video':
            counts['video'] += 1
        elif codec_type == 'audio':
            counts['audio'] += 1
        elif codec_type == 'subtitle':
            counts['subtitle'] += 1
        elif codec_type == 'data':
            counts['data'] += 1
    
    logger.info(f"Stream counts for {Path(video_file).name}: {counts}")
    return counts

def embed_multiple_subtitles(video_file, subtitle_files, output_file=None, languages=None, titles=None):
    """
    Embed multiple subtitle tracks into a video file
    
    - Copies ALL video streams from original file
    - Copies ALL audio streams from original file
    - REPLACES all original subtitles with new subtitle files
    - No re-encoding (fast processing)
    
    Args:
        video_file (str): Path to input video file
        subtitle_files (list): List of subtitle file paths
        output_file (str, optional): Path to output video file
        languages (list, optional): List of language codes (e.g., ['eng', 'spa', 'fre'])
        titles (list, optional): List of subtitle titles
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Validate input video file
    if not os.path.exists(video_file):
        logger.error(f"Video file not found: {video_file}")
        return False
    
    # Validate subtitle files
    if not subtitle_files or len(subtitle_files) == 0:
        logger.error("No subtitle files provided")
        return False
    
    for sub_file in subtitle_files:
        if not os.path.exists(sub_file):
            logger.error(f"Subtitle file not found: {sub_file}")
            return False
    
    # Convert to Path objects
    video_path = Path(video_file)
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = video_path.parent / f"{video_path.stem}_with_subtitles{video_path.suffix}"
    
    # Convert output to Path and ensure it's a clean path
    output_path = Path(output_file)
    
    # Log the paths for debugging
    logger.info(f"Input video path: {video_file}")
    logger.info(f"Output video path: {output_file}")
    
    # Ensure output directory exists
    if not ensure_output_directory(output_file):
        logger.error("Failed to create output directory")
        return False
    
    # Check if output path is valid
    if not output_path.parent.exists():
        logger.error(f"Output directory does not exist: {output_path.parent}")
        return False
    
    # Detect video container format
    video_ext = video_path.suffix.lower()
    is_mp4 = video_ext in ['.mp4', '.m4v']
    is_mkv = video_ext in ['.mkv', '.webm']
    
    # Get info about original video
    stream_counts = get_stream_count(video_file)
    if stream_counts:
        logger.info(f"Original video has: {stream_counts['video']} video, "
                   f"{stream_counts['audio']} audio, {stream_counts['subtitle']} subtitle streams")
    
    # Build FFmpeg command
    cmd = ['ffmpeg']
    
    # Add global options
    cmd.extend(['-hide_banner', '-loglevel', 'warning'])
    
    # Input video file
    cmd.extend(['-i', str(video_file)])
    
    # Add all subtitle files as inputs
    for sub_file in subtitle_files:
        cmd.extend(['-i', str(sub_file)])
    
    # Map ONLY video and audio streams from original file (excludes original subtitles)
    # The ? makes it optional - won't fail if stream type doesn't exist
    cmd.extend(['-map', '0:v?'])  # Map all video streams
    cmd.extend(['-map', '0:a?'])  # Map all audio streams
    # Intentionally NOT mapping 0:s (subtitle streams) - this removes original subtitles
    
    # Map all new subtitle inputs
    for i in range(len(subtitle_files)):
        cmd.extend(['-map', str(i + 1)])  # Map subtitle file (input index starts from 1)
    
    # Copy video streams without re-encoding (preserves quality and speed)
    cmd.extend(['-c:v', 'copy'])
    
    # Copy audio streams without re-encoding
    cmd.extend(['-c:a', 'copy'])
    
    # Set subtitle codec based on container format
    if is_mp4:
        # MP4 container requires mov_text codec for subtitles
        cmd.extend(['-c:s', 'mov_text'])
        logger.info("Using mov_text codec for MP4 container")
    elif is_mkv:
        # MKV supports multiple subtitle formats
        for i, sub_file in enumerate(subtitle_files):
            sub_format = get_subtitle_format(sub_file)
            if sub_format == 'ass':
                # Keep ASS format for styling
                cmd.extend([f'-c:s:{i}', 'ass'])
            else:
                # Use SRT for other formats
                cmd.extend([f'-c:s:{i}', 'srt'])
        logger.info("Using native subtitle codecs for MKV container")
    else:
        # For other containers, try SRT
        cmd.extend(['-c:s', 'srt'])
        logger.info(f"Using SRT codec for {video_ext} container")
    
    # Add metadata for each subtitle track
    for i, sub_file in enumerate(subtitle_files):
        # Set language code
        lang = languages[i] if languages and i < len(languages) else 'und'
        cmd.extend([f'-metadata:s:s:{i}', f'language={lang}'])
        
        # Set title
        if titles and i < len(titles):
            title = titles[i]
        else:
            # Use filename without extension as default title
            title = Path(sub_file).stem
        cmd.extend([f'-metadata:s:s:{i}', f'title={title}'])
        
        # Set first subtitle as default
        if i == 0:
            cmd.extend([f'-disposition:s:{i}', 'default'])
        else:
            cmd.extend([f'-disposition:s:{i}', '0'])
    
    # Additional options for better compatibility
    cmd.extend([
        '-movflags', '+faststart',  # Enable fast start for MP4 (web streaming)
        '-max_muxing_queue_size', '9999',  # Prevent muxing queue overflow
        '-y'  # Overwrite output file without asking
    ])
    
    # Add output file (ensure it's a string)
    cmd.append(str(output_file))
    
    # Log processing information
    logger.info("="*60)
    logger.info("Starting subtitle embedding process")
    logger.info(f"Input video: {video_file}")
    logger.info(f"Number of subtitle tracks: {len(subtitle_files)}")
    for i, sub_file in enumerate(subtitle_files):
        lang = languages[i] if languages and i < len(languages) else 'und'
        logger.info(f"  [{i+1}] {Path(sub_file).name} (language: {lang})")
    logger.info(f"Output video: {output_file}")
    logger.info(f"Container format: {video_ext}")
    logger.info("="*60)
    
    # Log FFmpeg command for debugging
    logger.debug(f"FFmpeg command: {' '.join(cmd)}")
    
    try:
        # Execute FFmpeg command
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3600  # 1 hour timeout for large files
        )
        
        if result.returncode == 0:
            # Check if output file was created
            if os.path.exists(output_file):
                output_size = os.path.getsize(output_file)
                logger.info(f"✓ Successfully created: {output_file}")
                logger.info(f"✓ Output file size: {output_size / (1024*1024):.2f} MB")
                
                # Verify output file has the expected streams
                output_counts = get_stream_count(output_file)
                if output_counts:
                    logger.info(f"✓ Output video has: {output_counts['video']} video, "
                              f"{output_counts['audio']} audio, {output_counts['subtitle']} subtitle streams")
                
                return True
            else:
                logger.error(f"✗ Output file was not created: {output_file}")
                logger.error(f"Expected output path: {output_file}")
                logger.error(f"Output directory exists: {output_path.parent.exists()}")
                logger.error(f"Output directory writable: {os.access(output_path.parent, os.W_OK)}")
                return False
        else:
            logger.error("✗ FFmpeg processing failed")
            logger.error(f"Return code: {result.returncode}")
            
            # Log stderr for debugging
            if result.stderr:
                # Only log last 50 lines to avoid spam
                stderr_lines = result.stderr.split('\n')
                logger.error("FFmpeg stderr (last 50 lines):")
                for line in stderr_lines[-50:]:
                    if line.strip():
                        logger.error(f"  {line}")
            
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("✗ FFmpeg process timeout (exceeded 1 hour)")
        return False
    except Exception as e:
        logger.error(f"✗ Exception during FFmpeg processing: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def validate_subtitle_file(subtitle_file):
    """
    Validate subtitle file format and readability
    
    Args:
        subtitle_file: Path to subtitle file
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(subtitle_file):
        logger.error(f"Subtitle file not found: {subtitle_file}")
        return False
    
    # Check file size
    file_size = os.path.getsize(subtitle_file)
    if file_size == 0:
        logger.error(f"Subtitle file is empty: {subtitle_file}")
        return False
    
    if file_size > 10 * 1024 * 1024:  # 10 MB
        logger.warning(f"Subtitle file is very large ({file_size / (1024*1024):.2f} MB): {subtitle_file}")
    
    # Check file extension
    ext = Path(subtitle_file).suffix.lower()
    valid_extensions = ['.srt', '.ass', '.ssa', '.vtt', '.sub']
    if ext not in valid_extensions:
        logger.error(f"Unsupported subtitle format: {ext}")
        return False
    
    # Try to read first few lines
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if not first_line:
                logger.error(f"Could not read subtitle file: {subtitle_file}")
                return False
    except Exception as e:
        logger.error(f"Error reading subtitle file: {e}")
        return False
    
    logger.debug(f"Subtitle file validated: {subtitle_file}")
    return True

def get_ffmpeg_version():
    """
    Get FFmpeg version information
    
    Returns:
        str: FFmpeg version string or None if not available
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # First line contains version
            version_line = result.stdout.split('\n')[0]
            return version_line
        return None
    except Exception as e:
        logger.error(f"Error getting FFmpeg version: {e}")
        return None

def cleanup_temp_files(*file_paths):
    """
    Clean up temporary files
    
    Args:
        *file_paths: Variable number of file paths to delete
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete temp file {file_path}: {e}")

# Initialize and check dependencies on import
if __name__ != '__main__':
    ffmpeg_available = check_ffmpeg()
    ffprobe_available = check_ffprobe()
    
    if ffmpeg_available and ffprobe_available:
        version = get_ffmpeg_version()
        if version:
            logger.info(f"Subtitle embedder initialized with {version}")
    else:
        logger.warning("Subtitle embedder initialized but FFmpeg/FFprobe not available")
