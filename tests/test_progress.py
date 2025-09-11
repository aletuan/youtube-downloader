#!/usr/bin/env python3
"""Unit tests for progress tracking functionality"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.progress import DownloadProgress, ProgressTracker, create_console_progress_callback


class TestDownloadProgress(unittest.TestCase):
    """Test cases for DownloadProgress data class"""
    
    def test_download_progress_initialization(self):
        """Test default initialization of DownloadProgress"""
        progress = DownloadProgress()
        
        self.assertEqual(progress.status, "starting")
        self.assertEqual(progress.percent, 0.0)
        self.assertEqual(progress.downloaded_bytes, 0)
        self.assertIsNone(progress.total_bytes)
        self.assertIsNone(progress.speed)
        self.assertIsNone(progress.eta)
        self.assertIsNone(progress.filename)
        self.assertEqual(progress.elapsed, 0.0)
    
    def test_percent_str_formatting(self):
        """Test percentage string formatting"""
        progress = DownloadProgress(percent=45.67)
        self.assertEqual(progress.percent_str, "45.7%")
        
        progress = DownloadProgress(percent=0.0)
        self.assertEqual(progress.percent_str, "0.0%")
        
        progress = DownloadProgress(percent=100.0)
        self.assertEqual(progress.percent_str, "100.0%")
    
    def test_speed_str_formatting(self):
        """Test speed string formatting"""
        # Test bytes per second
        progress = DownloadProgress(speed=512)
        self.assertEqual(progress.speed_str, "512 B/s")
        
        # Test kilobytes per second
        progress = DownloadProgress(speed=1536)  # 1.5 KB/s
        self.assertEqual(progress.speed_str, "1.5 KB/s")
        
        # Test megabytes per second
        progress = DownloadProgress(speed=2097152)  # 2.0 MB/s
        self.assertEqual(progress.speed_str, "2.0 MB/s")
        
        # Test gigabytes per second
        progress = DownloadProgress(speed=1073741824)  # 1.0 GB/s
        self.assertEqual(progress.speed_str, "1.0 GB/s")
        
        # Test no speed
        progress = DownloadProgress(speed=None)
        self.assertEqual(progress.speed_str, "-- B/s")
    
    def test_size_str_formatting(self):
        """Test size string formatting"""
        # Test bytes
        progress = DownloadProgress(downloaded_bytes=512, total_bytes=1024)
        self.assertEqual(progress.size_str, "512 B / 1.0 KB")
        
        # Test kilobytes
        progress = DownloadProgress(downloaded_bytes=512000, total_bytes=1024000)
        self.assertEqual(progress.size_str, "500.0 KB / 1000.0 KB")
        
        # Test megabytes
        progress = DownloadProgress(downloaded_bytes=1048576, total_bytes=2097152)
        self.assertEqual(progress.size_str, "1.0 MB / 2.0 MB")
        
        # Test unknown total
        progress = DownloadProgress(downloaded_bytes=1048576, total_bytes=None)
        self.assertEqual(progress.size_str, "1.0 MB / ??")
    
    def test_eta_str_formatting(self):
        """Test ETA string formatting"""
        # Test seconds only
        progress = DownloadProgress(eta=45)
        self.assertEqual(progress.eta_str, "00:45")
        
        # Test minutes and seconds
        progress = DownloadProgress(eta=125)  # 2:05
        self.assertEqual(progress.eta_str, "02:05")
        
        # Test hours, minutes, and seconds
        progress = DownloadProgress(eta=3725)  # 1:02:05
        self.assertEqual(progress.eta_str, "01:02:05")
        
        # Test no ETA
        progress = DownloadProgress(eta=None)
        self.assertEqual(progress.eta_str, "--:--")


class TestProgressTracker(unittest.TestCase):
    """Test cases for ProgressTracker class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.callback_calls = []
        
        def test_callback(progress):
            self.callback_calls.append(progress)
        
        self.test_callback = test_callback
        self.tracker = ProgressTracker(self.test_callback)
    
    def test_progress_tracker_initialization(self):
        """Test ProgressTracker initialization"""
        tracker = ProgressTracker()
        self.assertIsNone(tracker.progress_callback)
        self.assertIsNone(tracker.start_time)
        self.assertEqual(tracker.current_progress.status, "starting")
    
    def test_create_progress_hook(self):
        """Test progress hook creation"""
        hook = self.tracker.create_progress_hook()
        self.assertTrue(callable(hook))
    
    @patch('time.time')
    def test_progress_hook_downloading(self, mock_time):
        """Test progress hook with downloading status"""
        mock_time.return_value = 1000.0
        
        hook = self.tracker.create_progress_hook()
        
        # Simulate yt-dlp progress data
        progress_data = {
            'status': 'downloading',
            'downloaded_bytes': 512000,
            'total_bytes': 1024000,
            'speed': 100000,
            'eta': 5,
            'filename': 'test_video.mp4'
        }
        
        hook(progress_data)
        
        # Verify progress was updated
        progress = self.tracker.get_current_progress()
        self.assertEqual(progress.status, 'downloading')
        self.assertEqual(progress.downloaded_bytes, 512000)
        self.assertEqual(progress.total_bytes, 1024000)
        self.assertEqual(progress.speed, 100000)
        self.assertEqual(progress.eta, 5)
        self.assertEqual(progress.filename, 'test_video.mp4')
        self.assertAlmostEqual(progress.percent, 50.0, places=1)
        
        # Verify callback was called
        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(self.callback_calls[0].status, 'downloading')
    
    @patch('time.time')
    def test_progress_hook_finished(self, mock_time):
        """Test progress hook with finished status"""
        mock_time.return_value = 1005.0  # 5 seconds elapsed
        
        # Set up some initial progress and start time
        self.tracker.start_time = 1000.0  # Started 5 seconds ago
        self.tracker.current_progress.total_bytes = 1024000
        
        hook = self.tracker.create_progress_hook()
        
        # Simulate finished download
        progress_data = {
            'status': 'finished',
            'filename': 'test_video.mp4'
        }
        
        hook(progress_data)
        
        # Verify progress was updated
        progress = self.tracker.get_current_progress()
        self.assertEqual(progress.status, 'finished')
        self.assertEqual(progress.percent, 100.0)
        self.assertEqual(progress.filename, 'test_video.mp4')
        self.assertEqual(progress.elapsed, 5.0)
        
        # Verify callback was called
        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(self.callback_calls[0].status, 'finished')
    
    @patch('time.time')
    def test_progress_hook_error(self, mock_time):
        """Test progress hook with error status"""
        mock_time.return_value = 1003.0  # 3 seconds elapsed
        
        # Set start time to simulate download that has been running
        self.tracker.start_time = 1000.0  # Started 3 seconds ago
        
        hook = self.tracker.create_progress_hook()
        
        # Simulate error
        progress_data = {
            'status': 'error'
        }
        
        hook(progress_data)
        
        # Verify progress was updated
        progress = self.tracker.get_current_progress()
        self.assertEqual(progress.status, 'error')
        self.assertEqual(progress.elapsed, 3.0)
        
        # Verify callback was called
        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(self.callback_calls[0].status, 'error')
    
    def test_progress_hook_callback_exception(self):
        """Test that callback exceptions don't break the hook"""
        def failing_callback(progress):
            raise Exception("Callback failed")
        
        tracker = ProgressTracker(failing_callback)
        hook = tracker.create_progress_hook()
        
        # Should not raise an exception
        progress_data = {
            'status': 'downloading',
            'downloaded_bytes': 100,
            'total_bytes': 200
        }
        
        try:
            hook(progress_data)
        except Exception:
            self.fail("Progress hook should handle callback exceptions gracefully")
    
    def test_reset_functionality(self):
        """Test progress tracker reset"""
        # Set some progress
        self.tracker.start_time = 1000.0
        self.tracker.current_progress = DownloadProgress(
            status="downloading",
            percent=50.0,
            downloaded_bytes=500
        )
        
        # Reset the tracker
        self.tracker.reset()
        
        # Verify reset
        self.assertIsNone(self.tracker.start_time)
        self.assertEqual(self.tracker.current_progress.status, "starting")
        self.assertEqual(self.tracker.current_progress.percent, 0.0)
        self.assertEqual(self.tracker.current_progress.downloaded_bytes, 0)


class TestConsoleProgressCallback(unittest.TestCase):
    """Test cases for console progress callback"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.callback = create_console_progress_callback()
    
    @patch('builtins.print')
    def test_console_callback_downloading(self, mock_print):
        """Test console callback with downloading progress"""
        progress = DownloadProgress(
            status="downloading",
            percent=45.5,
            downloaded_bytes=500000,
            total_bytes=1000000,
            speed=50000,
            eta=10
        )
        
        self.callback(progress)
        
        # Verify print was called with progress info
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn("⬇️", call_args)
        self.assertIn("45.5%", call_args)
        self.assertIn("48.8 KB/s", call_args)
        self.assertIn("ETA: 00:10", call_args)
    
    @patch('builtins.print')
    def test_console_callback_finished(self, mock_print):
        """Test console callback with finished status"""
        progress = DownloadProgress(
            status="finished",
            downloaded_bytes=1000000,
            total_bytes=1000000,
            elapsed=15.5
        )
        
        self.callback(progress)
        
        # Verify print was called with completion message
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn("✅", call_args)
        self.assertIn("Download completed", call_args)
        self.assertIn("15.5s", call_args)
    
    @patch('builtins.print')
    def test_console_callback_error(self, mock_print):
        """Test console callback with error status"""
        progress = DownloadProgress(
            status="error",
            elapsed=8.2
        )
        
        self.callback(progress)
        
        # Verify print was called with error message
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn("❌", call_args)
        self.assertIn("Download failed", call_args)
        self.assertIn("8.2s", call_args)


if __name__ == '__main__':
    unittest.main(verbosity=2)