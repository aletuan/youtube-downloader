#!/usr/bin/env python3
import yt_dlp
from pathlib import Path
import re

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_youtube_video(url, output_dir="download-data"):
    """Download a YouTube video with subtitles using yt-dlp"""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # First, get video info to create folder name
    info_opts = {'quiet': True}
    try:
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = sanitize_filename(info.get('title', 'Unknown'))
            video_id = info.get('id', 'unknown')
            
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return
    
    # Create folder for this specific video
    video_folder = Path(output_dir) / f"{video_title}_{video_id}"
    video_folder.mkdir(exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': str(video_folder / '%(title)s.%(ext)s'),
        'format': 'best',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'en-US'],
        'subtitlesformat': 'vtt',
    }
    
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