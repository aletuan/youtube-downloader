#!/usr/bin/env python3
"""Validation utilities for YouTube downloader"""

from pathlib import Path
from typing import Tuple, Optional


def validate_youtube_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if the URL is a valid YouTube URL
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not url or not url.strip():
        return False, "Please enter a YouTube URL"
    
    url = url.strip()
    valid_prefixes = ('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/')
    
    if not url.startswith(valid_prefixes):
        return False, "Please enter a valid YouTube URL"
    
    return True, None


def validate_output_directory(output_dir: str) -> Tuple[bool, Optional[str]]:
    """
    Validate and prepare output directory
    
    Args:
        output_dir: Directory path to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not output_dir or not output_dir.strip():
        return False, "Please specify an output directory"
    
    output_path = Path(output_dir.strip())
    
    # Try to create directory if it doesn't exist
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        return True, None
    except Exception as e:
        return False, f"Cannot create output directory: {str(e)}"


def classify_error_type(error_msg: str) -> str:
    """
    Classify error message into user-friendly categories
    
    Args:
        error_msg: Error message to classify
        
    Returns:
        Classified error message
    """
    error_msg_lower = error_msg.lower()
    
    if "network" in error_msg_lower or "connection" in error_msg_lower:
        return "❌ Network error: Check your internet connection"
    elif "permission" in error_msg_lower:
        return "❌ Permission error: Check folder write permissions"
    elif "not found" in error_msg_lower:
        return "❌ Video not found: Invalid URL or private video"
    elif "429" in error_msg or "too many requests" in error_msg_lower:
        return "❌ Rate limited: Try again in a few minutes"
    else:
        return f"❌ Error: {error_msg}"


def is_network_error(error_msg: str) -> bool:
    """Check if error is network-related"""
    error_msg_lower = error_msg.lower()
    return "network" in error_msg_lower or "connection" in error_msg_lower


def is_permission_error(error_msg: str) -> bool:
    """Check if error is permission-related"""
    return "permission" in error_msg.lower()


def is_not_found_error(error_msg: str) -> bool:
    """Check if error is not found related"""
    return "not found" in error_msg.lower()