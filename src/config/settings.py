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
TRANSLATION_BATCH_SIZE = 50  # Optimized batch size for better performance
TRANSLATION_RATE_LIMIT_DELAY = 0.5  # Reduced delay for faster processing
TRANSLATION_MAX_TOKENS = 8000  # Maximum tokens per API call
TRANSLATION_TIMEOUT = 60  # Timeout per batch in seconds