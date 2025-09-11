#!/usr/bin/env python3
"""Configuration settings for YouTube downloader"""

# Download settings
DEFAULT_OUTPUT_DIR = "download-data"
SUBTITLE_LANGUAGES = ['en', 'en-US']
SUBTITLE_FORMAT = 'vtt'
VIDEO_FORMAT = 'best'

# yt-dlp configuration
YT_DLP_INFO_OPTIONS = {'quiet': True}