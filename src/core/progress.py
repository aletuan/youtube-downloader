#!/usr/bin/env python3
"""Download progress tracking utilities for YouTube downloader"""

import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class DownloadProgress:
    """Data class to represent download progress information"""
    status: str = "starting"
    percent: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[float] = None
    eta: Optional[int] = None
    filename: Optional[str] = None
    elapsed: float = 0.0
    
    @property
    def percent_str(self) -> str:
        """Get formatted percentage string"""
        return f"{self.percent:.1f}%" if self.percent else "0.0%"
    
    @property
    def speed_str(self) -> str:
        """Get formatted speed string"""
        if not self.speed:
            return "-- B/s"
        
        if self.speed < 1024:
            return f"{self.speed:.0f} B/s"
        elif self.speed < 1024 * 1024:
            return f"{self.speed/1024:.1f} KB/s"
        elif self.speed < 1024 * 1024 * 1024:
            return f"{self.speed/(1024*1024):.1f} MB/s"
        else:
            return f"{self.speed/(1024*1024*1024):.1f} GB/s"
    
    @property
    def size_str(self) -> str:
        """Get formatted size string"""
        def format_bytes(bytes_val):
            if not bytes_val:
                return "-- B"
            if bytes_val < 1024:
                return f"{bytes_val} B"
            elif bytes_val < 1024 * 1024:
                return f"{bytes_val/1024:.1f} KB"
            elif bytes_val < 1024 * 1024 * 1024:
                return f"{bytes_val/(1024*1024):.1f} MB"
            else:
                return f"{bytes_val/(1024*1024*1024):.1f} GB"
        
        downloaded = format_bytes(self.downloaded_bytes)
        total = format_bytes(self.total_bytes) if self.total_bytes else "??"
        return f"{downloaded} / {total}"
    
    @property
    def eta_str(self) -> str:
        """Get formatted ETA string"""
        if not self.eta:
            return "--:--"
        
        minutes = self.eta // 60
        seconds = self.eta % 60
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class ProgressTracker:
    """Thread-safe progress tracker for yt-dlp downloads"""
    
    def __init__(self, progress_callback: Optional[Callable[[DownloadProgress], None]] = None):
        """
        Initialize progress tracker
        
        Args:
            progress_callback: Optional callback function to receive progress updates
        """
        self.progress_callback = progress_callback
        self.start_time = None
        self.current_progress = DownloadProgress()
    
    def create_progress_hook(self):
        """
        Create a progress hook function for yt-dlp
        
        Returns:
            Function that can be used as yt-dlp progress hook
        """
        def progress_hook(d: Dict[str, Any]):
            """yt-dlp progress hook function"""
            
            if self.start_time is None:
                self.start_time = time.time()
            
            status = d.get('status', 'unknown')
            elapsed = time.time() - self.start_time
            
            if status == 'downloading':
                # Extract progress information from yt-dlp data
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                speed = d.get('speed')
                eta = d.get('eta')
                filename = d.get('filename', '')
                
                # Calculate percentage
                percent = 0.0
                if total and total > 0:
                    percent = (downloaded / total) * 100
                
                # Update progress data
                self.current_progress = DownloadProgress(
                    status=status,
                    percent=percent,
                    downloaded_bytes=downloaded,
                    total_bytes=total,
                    speed=speed,
                    eta=eta,
                    filename=filename,
                    elapsed=elapsed
                )
                
            elif status == 'finished':
                # Download completed
                filename = d.get('filename', '')
                self.current_progress = DownloadProgress(
                    status='finished',
                    percent=100.0,
                    downloaded_bytes=self.current_progress.total_bytes or 0,
                    total_bytes=self.current_progress.total_bytes,
                    filename=filename,
                    elapsed=elapsed
                )
                
            elif status == 'error':
                # Download error occurred
                self.current_progress = DownloadProgress(
                    status='error',
                    elapsed=elapsed
                )
            
            # Call the callback if provided
            if self.progress_callback:
                try:
                    self.progress_callback(self.current_progress)
                except Exception:
                    # Don't let callback errors break the download
                    pass
        
        return progress_hook
    
    def get_current_progress(self) -> DownloadProgress:
        """Get the current progress state"""
        return self.current_progress
    
    def reset(self):
        """Reset the progress tracker"""
        self.start_time = None
        self.current_progress = DownloadProgress()


def create_console_progress_callback() -> Callable[[DownloadProgress], None]:
    """
    Create a simple console progress callback for CLI usage
    
    Returns:
        Callback function that prints progress to console
    """
    def console_callback(progress: DownloadProgress):
        if progress.status == 'downloading':
            print(f"\r⬇️  {progress.percent_str} | {progress.size_str} | {progress.speed_str} | ETA: {progress.eta_str}", 
                  end='', flush=True)
        elif progress.status == 'finished':
            print(f"\n✅ Download completed! ({progress.size_str} in {progress.elapsed:.1f}s)")
        elif progress.status == 'error':
            print(f"\n❌ Download failed after {progress.elapsed:.1f}s")
    
    return console_callback