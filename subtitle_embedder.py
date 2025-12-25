#!/usr/bin/env python3
"""
Subtitle Embedder - Complete Bot Compatible Version
Copies only video and audio streams, replaces original subtitles with new ones
Fixed output path handling, subtitle encoding, and stream mapping
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
    
    # ========== VALIDATION PHASE ==========
    
    # Validate input video file exists
    if not os.path.exists(video_file):
        logger.error(f"Video file not found: {video_file}")
        return False
    
    # Validate subtitle files list is not empty
    if not subtitle_files or len(subtitle_files) == 0:
        logger.error("No subtitle files provided")
        return False
    
    # Validate each subtitle file exists
    for sub_file in subtitle_files:
        if not os.path.exists(sub_file):
            logger.error(f"Subtitle file not found: {sub_file}")
            return False
    
    # ========== PATH SETUP PHASE ==========
    
    # Convert to Path objects for safer handling
    video_path = Path(video_file).resolve()  # resolve() gets absolute path
    
    # Generate output filename if not provided
    if output_file is None:
        # Default: add "_with_subtitles" suffix to original filename
        output_file = video_path.parent / f"{video_path.stem}_with_subtitles{video_path.suffix}"
    
    # Convert output to Path and resolve to absolute path
    output_path = Path(output_file).resolve()
    
    # Log the paths for debugging
    logger.info(f"Input video path: {video_path}")
    logger.info(f"Output video path: {output_path}")
    
    # Ensure output directory exists (create if needed)
    if not ensure_output_directory(output_path):
        logger.error("Failed to create output directory")
        return False
    
    # Double-check output directory exists after creation
    if not output_path.parent.exists():
        logger.error(f"Output directory does not exist: {output_path.parent}")
        return False
    
    # Check if output directory is writable
    if not os.access(output_path.parent, os.W_OK):
        logger.error(f"Output directory is not writable: {output_path.parent}")
        return False
    
    # ========== CONTAINER FORMAT DETECTION ==========
    
    # Detect video container format from extension
    video_ext = video_path.suffix.lower()
    is_mp4 = video_ext in ['.mp4', '.m4v']
    is_mkv = video_ext in ['.mkv', '.webm']
    
    logger.info(f"Container format: {video_ext} (MP4: {is_mp4}, MKV: {is_mkv})")
    
    # ========== VIDEO STREAM ANALYSIS ==========
    
    # Get info about original video streams
    stream_counts = get_stream_count(str(video_path))
    if stream_counts:
        logger.info(f"Original video has: {stream_counts['video']} video, "
                   f"{stream_counts['audio']} audio, {stream_counts['subtitle']} subtitle streams")
    
    # ========== FFMPEG COMMAND CONSTRUCTION ==========
    
    # Start building FFmpeg command
    cmd = ['ffmpeg']
    
    # Add global options
    cmd.extend([
        '-hide_banner',           # Hide FFmpeg banner
        '-loglevel', 'warning',   # Show only warnings and errors
        '-nostdin',               # Disable stdin interaction (important for bots)
        '-y'                      # Overwrite output file without asking
    ])
    
    # Input video file
    cmd.extend(['-i', str(video_path)])
    
    # Add all subtitle files as inputs with UTF-8 encoding enforcement
    for sub_file in subtitle_files:
        # Force UTF-8 encoding for subtitle files to prevent corruption
        cmd.extend([
            '-sub_charenc', 'UTF-8',  # Set subtitle character encoding to UTF-8
            '-i', str(Path(sub_file).resolve())
        ])
    
    # ========== STREAM MAPPING (CRITICAL SECTION) ==========
    
    # Map ONLY video and audio streams from original file
    # This EXCLUDES original subtitle streams (they will be replaced)
    
    # The '?' makes mapping optional - won't fail if stream type doesn't exist
    cmd.extend(['-map', '0:v?'])  # Map all video streams from input 0
    cmd.extend(['-map', '0:a?'])  # Map all audio streams from input 0
    
    # NOTE: We are NOT mapping 0:s (subtitle streams)
    # This effectively removes all original subtitles
    
    # Map all new subtitle inputs
    # Subtitle files start from input index 1 (0 is the video)
    for i in range(len(subtitle_files)):
        cmd.extend(['-map', str(i + 1)])  # Map subtitle file i+1
    
    # ========== CODEC CONFIGURATION ==========
    
    # Copy video streams without re-encoding (preserves quality, faster processing)
    cmd.extend(['-c:v', 'copy'])
    
    # Copy audio streams without re-encoding
    cmd.extend(['-c:a', 'copy'])
    
    # ========== SUBTITLE CODEC SELECTION ==========
    
    # Subtitle codec depends on container format
    if is_mp4:
        # MP4 container REQUIRES mov_text codec for subtitles
        # Other subtitle formats will cause player compatibility issues
        cmd.extend(['-c:s', 'mov_text'])
        logger.info("Using mov_text codec for MP4 container")
        
    elif is_mkv:
        # MKV supports multiple subtitle formats natively
        # We can preserve ASS/SSA styling for better subtitle appearance
        for i, sub_file in enumerate(subtitle_files):
            sub_format = get_subtitle_format(sub_file)
            
            if sub_format == 'ass':
                # Keep ASS format to preserve styling (colors, fonts, positions)
                cmd.extend([f'-c:s:{i}', 'ass'])
                logger.info(f"Subtitle {i+1}: Using ASS codec (preserves styling)")
            else:
                # Use SRT for other formats (most compatible)
                cmd.extend([f'-c:s:{i}', 'srt'])
                logger.info(f"Subtitle {i+1}: Using SRT codec")
        
    else:
        # For other containers (AVI, FLV, etc.), default to SRT
        cmd.extend(['-c:s', 'srt'])
        logger.info(f"Using SRT codec for {video_ext} container")
    
    # ========== SUBTITLE METADATA CONFIGURATION ==========
    
    # Add metadata for each subtitle track
    for i, sub_file in enumerate(subtitle_files):
        # Set language code (ISO 639-2 format: eng, spa, fre, etc.)
        lang = languages[i] if languages and i < len(languages) else 'und'
        cmd.extend([f'-metadata:s:s:{i}', f'language={lang}'])
        
        # Set subtitle track title (shown in player)
        if titles and i < len(titles):
            title = titles[i]
        else:
            # Use filename without extension as default title
            title = Path(sub_file).stem
        cmd.extend([f'-metadata:s:s:{i}', f'title={title}'])
        
        # Set disposition (default/forced flags)
        if i == 0:
            # First subtitle is marked as default (auto-selected in player)
            cmd.extend([f'-disposition:s:{i}', 'default'])
        else:
            # Other subtitles are not default (user must manually select)
            cmd.extend([f'-disposition:s:{i}', '0'])
    
    # ========== ADDITIONAL OPTIONS FOR COMPATIBILITY ==========
    
    cmd.extend([
        '-movflags', '+faststart',          # Enable fast start for MP4 (web streaming optimization)
        '-max_muxing_queue_size', '9999',   # Prevent muxing queue overflow (fixes async issues)
    ])
    
    # Add output file (convert to string to ensure compatibility)
    cmd.append(str(output_path))
    
    # ========== LOGGING ==========
    
    logger.info("="*60)
    logger.info("Starting subtitle embedding process")
    logger.info(f"Input video: {video_path}")
    logger.info(f"Number of subtitle tracks: {len(subtitle_files)}")
    for i, sub_file in enumerate(subtitle_files):
        lang = languages[i] if languages and i < len(languages) else 'und'
        logger.info(f"  [{i+1}] {Path(sub_file).name} (language: {lang})")
    logger.info(f"Output video: {output_path}")
    logger.info(f"Container format: {video_ext}")
    logger.info("="*60)
    
    # Log FFmpeg command for debugging (only in debug mode)
    logger.debug(f"FFmpeg command: {' '.join(cmd)}")
    
    # ========== FFMPEG EXECUTION ==========
    
    try:
        # Execute FFmpeg command with timeout protection
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3600  # 1 hour timeout for large files
        )
        
        # ========== RESULT VERIFICATION ==========
        
        if result.returncode == 0:
            # FFmpeg succeeded, verify output file was created
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                logger.info(f"✓ Successfully created: {output_path}")
                logger.info(f"✓ Output file size: {output_size / (1024*1024):.2f} MB")
                
                # Verify output file has the expected streams
                output_counts = get_stream_count(str(output_path))
                if output_counts:
                    logger.info(f"✓ Output video has: {output_counts['video']} video, "
                              f"{output_counts['audio']} audio, {output_counts['subtitle']} subtitle streams")
                    
                    # Verify subtitle count matches expected
                    if output_counts['subtitle'] != len(subtitle_files):
                        logger.warning(f"⚠ Expected {len(subtitle_files)} subtitles, but found {output_counts['subtitle']}")
                
                return True
            else:
                # FFmpeg succeeded but file doesn't exist (rare edge case)
                logger.error(f"✗ Output file was not created: {output_path}")
                logger.error(f"Expected output path: {output_path}")
                logger.error(f"Output directory exists: {output_path.parent.exists()}")
                logger.error(f"Output directory writable: {os.access(output_path.parent, os.W_OK)}")
                return False
        else:
            # FFmpeg failed, log detailed error information
            logger.error("✗ FFmpeg processing failed")
            logger.error(f"Return code: {result.returncode}")
            
            # Log stderr for debugging (last 50 lines to avoid spam)
            if result.stderr:
                stderr_lines = result.stderr.split('\n')
                logger.error("FFmpeg stderr (last 50 lines):")
                for line in stderr_lines[-50:]:
                    if line.strip():
                        logger.error(f"  {line}")
            
            return False
            
    except subprocess.TimeoutExpired:
        # FFmpeg process exceeded timeout
        logger.error("✗ FFmpeg process timeout (exceeded 1 hour)")
        logger.error("This usually happens with extremely large files or system resource issues")
        return False
        
    except Exception as e:
        # Unexpected exception during FFmpeg execution
        logger.error(f"✗ Exception during FFmpeg processing: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        
        # Log full traceback for debugging
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
    # Check file exists
    if not os.path.exists(subtitle_file):
        logger.error(f"Subtitle file not found: {subtitle_file}")
        return False
    
    # Check file is not empty
    file_size = os.path.getsize(subtitle_file)
    if file_size == 0:
        logger.error(f"Subtitle file is empty: {subtitle_file}")
        return False
    
    # Warn if file is unusually large (might be corrupt or wrong file)
    if file_size > 10 * 1024 * 1024:  # 10 MB
        logger.warning(f"Subtitle file is very large ({file_size / (1024*1024):.2f} MB): {subtitle_file}")
    
    # Check file extension is valid
    ext = Path(subtitle_file).suffix.lower()
    valid_extensions = ['.srt', '.ass', '.ssa', '.vtt', '.sub']
    if ext not in valid_extensions:
        logger.error(f"Unsupported subtitle format: {ext}")
        return False
    
    # Try to read first few lines to ensure file is readable
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if not first_line:
                logger.error(f"Could not read subtitle file: {subtitle_file}")
                return False
    except UnicodeDecodeError:
        # File is not UTF-8, try with latin-1 or other encodings
        logger.warning(f"Subtitle file is not UTF-8 encoded: {subtitle_file}")
        try:
            with open(subtitle_file, 'r', encoding='latin-1') as f:
                first_line = f.readline()
        except Exception as e:
            logger.error(f"Error reading subtitle file with alternate encoding: {e}")
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
