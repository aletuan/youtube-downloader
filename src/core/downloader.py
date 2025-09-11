#!/usr/bin/env python3
"""Core YouTube downloader functionality"""

import yt_dlp
from pathlib import Path

from core.utils import sanitize_filename
from config.settings import (
    DEFAULT_OUTPUT_DIR,
    SUBTITLE_LANGUAGES,
    SUBTITLE_FORMAT,
    VIDEO_FORMAT,
    YT_DLP_INFO_OPTIONS
)


def _get_video_info(url):
    """Extract video information without downloading"""
    with yt_dlp.YoutubeDL(YT_DLP_INFO_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = sanitize_filename(info.get('title', 'Unknown'))
        video_id = info.get('id', 'unknown')
        return video_title, video_id


def _create_video_folder(output_dir, video_title, video_id):
    """Create and return the folder path for a specific video"""
    Path(output_dir).mkdir(exist_ok=True)
    video_folder = Path(output_dir) / f"{video_title}_{video_id}"
    video_folder.mkdir(exist_ok=True)
    return video_folder


def _get_yt_dlp_options(video_folder):
    """Configure yt-dlp download options"""
    return {
        'outtmpl': str(video_folder / '%(title)s.%(ext)s'),
        'format': VIDEO_FORMAT,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': SUBTITLE_LANGUAGES,
        'subtitlesformat': SUBTITLE_FORMAT,
    }


def download_youtube_video(url, output_dir=DEFAULT_OUTPUT_DIR):
    """Download a YouTube video with subtitles using yt-dlp"""
    
    try:
        video_title, video_id = _get_video_info(url)
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return
    
    video_folder = _create_video_folder(output_dir, video_title, video_id)
    ydl_opts = _get_yt_dlp_options(video_folder)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Successfully downloaded video and subtitles to: {video_folder}")
        print(f"Video: {video_title}")
    except Exception as e:
        print(f"Error downloading video: {e}")


if __name__ == "__main__":
    # Example usage
    video_url = input("Enter YouTube URL: ")
    download_youtube_video(video_url)