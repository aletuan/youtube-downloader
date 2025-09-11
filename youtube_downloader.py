#!/usr/bin/env python3
"""
YouTube Downloader - Compatibility wrapper for backward compatibility

This file maintains the original interface while using the new modular structure.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import from new structure
from core.downloader import (
    download_youtube_video,
    _get_video_info,
    _create_video_folder,
    _get_yt_dlp_options
)
from core.utils import sanitize_filename

# Export the public API
__all__ = [
    'download_youtube_video',
    'sanitize_filename',
    '_get_video_info',
    '_create_video_folder', 
    '_get_yt_dlp_options'
]

if __name__ == "__main__":
    # Example usage
    video_url = input("Enter YouTube URL: ")
    download_youtube_video(video_url)