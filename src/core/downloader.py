#!/usr/bin/env python3
"""Core YouTube downloader functionality"""

import yt_dlp
import time
import random
from pathlib import Path
from typing import Optional, Callable

from core.utils import sanitize_filename
from core.progress import ProgressTracker, DownloadProgress
from config.settings import (
    DEFAULT_OUTPUT_DIR,
    SUBTITLE_LANGUAGES,
    SUBTITLE_FORMAT,
    VIDEO_FORMAT,
    YT_DLP_INFO_OPTIONS
)


def _get_video_info(url):
    """Extract video information without downloading"""
    # Enhanced info options with anti-bot measures
    info_options = {
        **YT_DLP_INFO_OPTIONS,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'sleep_interval': random.uniform(0.5, 2.0),  # Small delay for info extraction
    }
    
    with yt_dlp.YoutubeDL(info_options) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = sanitize_filename(info.get('title', 'Unknown'))
        video_id = info.get('id', 'unknown')
        return video_title, video_id


def _check_video_exists(output_dir, video_title, video_id):
    """Check if a video already exists in the output directory
    
    Returns:
        tuple: (exists: bool, video_folder: Path, existing_files: list)
    """
    video_folder = Path(output_dir) / f"{video_title}_{video_id}"
    
    if not video_folder.exists():
        return False, video_folder, []
    
    # Check for video files (common video extensions)
    video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv', '.m4v']
    existing_files = []
    
    for file_path in video_folder.iterdir():
        if file_path.is_file():
            # Check if it's a video file
            if any(file_path.suffix.lower() == ext for ext in video_extensions):
                existing_files.append(file_path.name)
    
    return len(existing_files) > 0, video_folder, existing_files


def _create_video_folder(output_dir, video_title, video_id):
    """Create and return the folder path for a specific video"""
    Path(output_dir).mkdir(exist_ok=True)
    video_folder = Path(output_dir) / f"{video_title}_{video_id}"
    video_folder.mkdir(exist_ok=True)
    return video_folder


def _get_yt_dlp_options(video_folder, retry_attempt=0, progress_hook=None):
    """Configure yt-dlp download options with anti-bot detection measures"""
    
    # Rotate user agents to avoid detection
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    ]
    
    selected_ua = user_agents[retry_attempt % len(user_agents)]
    
    options = {
        'outtmpl': str(video_folder / '%(title)s.%(ext)s'),
        'format': VIDEO_FORMAT,
        
        # Anti-bot detection headers
        'http_headers': {
            'User-Agent': selected_ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        
        # Rate limiting and retry settings
        'sleep_interval': random.uniform(1, 3),  # Random delay between requests
        'max_sleep_interval': 10,
        'sleep_interval_subtitles': random.uniform(2, 5),
        
        # Retry settings
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': False,
        
        # Subtitles with fallback
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': SUBTITLE_LANGUAGES,
        'subtitlesformat': SUBTITLE_FORMAT,
        
        # Additional anti-detection measures
        'extract_flat': False,
        'ignoreerrors': False,
        'no_warnings': False,
    }
    
    # Add progress hook if provided
    if progress_hook:
        options['progress_hooks'] = [progress_hook]
    
    # On retry attempts, be more conservative with subtitles
    if retry_attempt > 0:
        options.update({
            'writesubtitles': False,  # Skip subtitles on retry to avoid rate limits
            'writeautomaticsub': False,
            'sleep_interval': random.uniform(3, 8),  # Longer delays
            'sleep_interval_subtitles': random.uniform(5, 10),
        })
    
    # On final retry, minimal options
    if retry_attempt > 1:
        options.update({
            'format': 'best[height<=720]',  # Lower quality to reduce load
            'sleep_interval': random.uniform(5, 12),
        })
    
    return options


def download_youtube_video(url, output_dir=DEFAULT_OUTPUT_DIR, progress_callback: Optional[Callable[[DownloadProgress], None]] = None):
    """Download a YouTube video with subtitles using yt-dlp with anti-bot measures"""
    
    try:
        video_title, video_id = _get_video_info(url)
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return
    
    video_folder = _create_video_folder(output_dir, video_title, video_id)
    
    # Initialize progress tracker if callback provided
    progress_tracker = None
    if progress_callback:
        progress_tracker = ProgressTracker(progress_callback)
    
    # Retry with exponential backoff and different strategies
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Download attempt {attempt + 1}/{max_retries}")
            
            # Add random delay to avoid pattern detection
            if attempt > 0:
                delay = random.uniform(2 ** attempt, 2 ** (attempt + 1))  # Exponential backoff
                print(f"Waiting {delay:.1f} seconds before retry...")
                time.sleep(delay)
            
            # Get progress hook if available
            progress_hook = progress_tracker.create_progress_hook() if progress_tracker else None
            ydl_opts = _get_yt_dlp_options(video_folder, retry_attempt=attempt, progress_hook=progress_hook)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Build success message
            success_msg = f"Successfully downloaded video to: {video_folder}\nVideo: {video_title}"
            if attempt == 0:
                success_msg += " (with subtitles)"
            elif attempt == 1:
                success_msg += " (video only - subtitles skipped due to rate limit)"
            else:
                success_msg += " (reduced quality to avoid rate limit)"
            
            print(success_msg)
            return
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_msg or "Too Many Requests" in error_msg:
                if attempt < max_retries - 1:
                    print(f"Rate limited (attempt {attempt + 1}). Retrying with different strategy...")
                    continue
                else:
                    print("❌ Final attempt failed due to rate limiting.")
                    print("💡 Try again in a few minutes, or use a different network/VPN.")
            
            # Check if it's a subtitle-specific error
            elif "subtitle" in error_msg.lower():
                if attempt < max_retries - 1:
                    print(f"Subtitle error (attempt {attempt + 1}). Retrying without subtitles...")
                    continue
                else:
                    print("❌ Failed to download even without subtitles.")
            
            # Other errors
            else:
                if attempt < max_retries - 1:
                    print(f"Download error (attempt {attempt + 1}): {error_msg}")
                    print("Retrying with different settings...")
                    continue
            
            # If we get here, all retries failed
            print(f"❌ Download failed after {max_retries} attempts: {error_msg}")
            
            # Provide helpful suggestions
            if "429" in error_msg or "rate" in error_msg.lower():
                print("\n💡 YouTube rate limiting suggestions:")
                print("   • Wait 10-30 minutes before trying again")
                print("   • Try using a VPN or different network")
                print("   • Consider downloading during off-peak hours")
            elif "private" in error_msg.lower() or "unavailable" in error_msg.lower():
                print("\n💡 Video may be private, deleted, or region-locked")
            else:
                print(f"\n💡 Try updating yt-dlp: pip install --upgrade yt-dlp")


if __name__ == "__main__":
    # Example usage with progress tracking
    from core.progress import create_console_progress_callback
    
    video_url = input("Enter YouTube URL: ")
    progress_callback = create_console_progress_callback()
    download_youtube_video(video_url, progress_callback=progress_callback)