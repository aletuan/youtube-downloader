#!/usr/bin/env python3
"""Utility functions for YouTube downloader"""

import re


def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)