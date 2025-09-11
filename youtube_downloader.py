#!/usr/bin/env python3
import yt_dlp
from pathlib import Path

def download_youtube_video(url, output_dir="download-data"):
    """Download a YouTube video using yt-dlp"""
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'format': 'best',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Successfully downloaded video from: {url}")
    except Exception as e:
        print(f"Error downloading video: {e}")

if __name__ == "__main__":
    # Example usage
    video_url = input("Enter YouTube URL: ")
    download_youtube_video(video_url)