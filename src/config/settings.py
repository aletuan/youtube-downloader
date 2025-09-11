#!/usr/bin/env python3
"""Configuration settings for YouTube downloader"""

import os

# Download settings
DEFAULT_OUTPUT_DIR = "download-data"
SUBTITLE_LANGUAGES = ['en', 'en-US']
SUBTITLE_FORMAT = 'vtt'
VIDEO_FORMAT = 'best'

# yt-dlp configuration
YT_DLP_INFO_OPTIONS = {'quiet': True}

# Translation settings
TRANSLATION_ENABLED = True  # Enable/disable translation feature
TRANSLATION_TARGET_LANGUAGE = 'Vietnamese'  # Default target language
TRANSLATION_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Claude API key from environment
TRANSLATION_MODEL = 'claude-3-haiku-20240307'  # Claude model to use
TRANSLATION_BATCH_SIZE = 10  # Number of subtitles to translate per API call
TRANSLATION_RATE_LIMIT_DELAY = 1.0  # Seconds to wait between API calls