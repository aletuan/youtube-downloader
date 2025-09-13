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

# Translation settings - all configurable via environment variables
TRANSLATION_ENABLED = os.getenv('TRANSLATION_ENABLED', 'true').lower() == 'true'  # Enable/disable translation feature
TRANSLATION_TARGET_LANGUAGE = os.getenv('TRANSLATION_TARGET_LANGUAGE', 'Vietnamese')  # Default target language
TRANSLATION_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Claude API key from environment
TRANSLATION_MODEL = os.getenv('TRANSLATION_MODEL', 'claude-3-5-sonnet-20241022')  # Claude model to use
TRANSLATION_BATCH_SIZE = int(os.getenv('TRANSLATION_BATCH_SIZE', '100'))  # Increased batch size for Claude 3.5 Sonnet
TRANSLATION_RATE_LIMIT_DELAY = float(os.getenv('TRANSLATION_RATE_LIMIT_DELAY', '0.0'))  # No delay for faster processing
TRANSLATION_MAX_TOKENS = int(os.getenv('TRANSLATION_MAX_TOKENS', '8000'))  # Maximum tokens for Claude 3.5 Sonnet
TRANSLATION_TIMEOUT = int(os.getenv('TRANSLATION_TIMEOUT', '60'))  # Timeout per batch in seconds