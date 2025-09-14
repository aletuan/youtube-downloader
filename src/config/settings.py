#!/usr/bin/env python3
"""Configuration settings for YouTube downloader"""

import os
import platform
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_default_downloads_folder():
    """
    Get the default Downloads folder for the current operating system.
    
    Returns:
        str: Full path to the default Downloads folder
    """
    system = platform.system().lower()
    
    if system == "windows":
        # Windows: %USERPROFILE%\Downloads
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            downloads_path = Path(user_profile) / "Downloads"
        else:
            # Fallback to current directory
            downloads_path = Path.cwd() / "download-data"
    elif system == "darwin":
        # macOS: ~/Downloads
        home = Path.home()
        downloads_path = home / "Downloads"
    elif system == "linux":
        # Linux: ~/Downloads (most common)
        home = Path.home()
        downloads_path = home / "Downloads"
    else:
        # Unknown system - fallback to current directory
        downloads_path = Path.cwd() / "download-data"
    
    # Create a subdirectory for our app to keep downloads organized
    app_downloads_path = downloads_path / "youtube-downloader"
    
    return str(app_downloads_path)


# Download settings
DEFAULT_OUTPUT_DIR = get_default_downloads_folder()
SUBTITLE_LANGUAGES = ['en', 'en-US']
SUBTITLE_FORMAT = 'vtt'
VIDEO_FORMAT = 'best'

# yt-dlp configuration
YT_DLP_INFO_OPTIONS = {'quiet': True}

