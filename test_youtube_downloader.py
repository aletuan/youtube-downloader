#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the current directory to Python path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_downloader import sanitize_filename, download_youtube_video


class TestSanitizeFilename(unittest.TestCase):
    """Test cases for the sanitize_filename function"""
    
    def test_sanitize_basic_filename(self):
        """Test that normal filenames are unchanged"""
        result = sanitize_filename("normal_filename.txt")
        self.assertEqual(result, "normal_filename.txt")
    
    def test_sanitize_filename_with_spaces(self):
        """Test that spaces are preserved"""
        result = sanitize_filename("file with spaces.txt")
        self.assertEqual(result, "file with spaces.txt")
    
    def test_sanitize_filename_with_invalid_chars(self):
        """Test that invalid characters are replaced with underscores"""
        result = sanitize_filename('file<>:"/\\|?*.txt')
        self.assertEqual(result, "file_________.txt")
    
    def test_sanitize_filename_mixed_case(self):
        """Test filename with mixed valid and invalid characters"""
        result = sanitize_filename("My Video: Part 1 | Episode <2>")
        self.assertEqual(result, "My Video_ Part 1 _ Episode _2_")
    
    def test_sanitize_empty_filename(self):
        """Test empty filename"""
        result = sanitize_filename("")
        self.assertEqual(result, "")
    
    def test_sanitize_filename_only_invalid_chars(self):
        """Test filename with only invalid characters"""
        result = sanitize_filename('<>:"/\\|?*')
        self.assertEqual(result, "_________")


class TestDownloadYoutubeVideo(unittest.TestCase):
    """Test cases for the download_youtube_video function"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://www.youtube.com/watch?v=test123"
        self.mock_video_info = {
            'title': 'Test Video Title',
            'id': 'test123'
        }
    
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_yt_dlp):
        """Test successful video download"""
        # Mock the YoutubeDL context manager
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = self.mock_video_info
        mock_ydl_instance.download.return_value = None
        
        # Call the function
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify that YoutubeDL was called correctly
        self.assertEqual(mock_yt_dlp.call_count, 2)  # Once for info, once for download
        mock_ydl_instance.extract_info.assert_called_once_with(self.test_url, download=False)
        mock_ydl_instance.download.assert_called_once_with([self.test_url])
        
        # Verify that the video folder was created
        expected_folder = Path(self.temp_dir) / "Test Video Title_test123"
        self.assertTrue(expected_folder.exists())
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_video_with_invalid_title_chars(self, mock_yt_dlp):
        """Test video download with title containing invalid characters"""
        mock_video_info = {
            'title': 'Test Video: Part <1> | "Special"',
            'id': 'test123'
        }
        
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = mock_video_info
        mock_ydl_instance.download.return_value = None
        
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify that the folder name is sanitized
        expected_folder = Path(self.temp_dir) / "Test Video_ Part _1_ _ _Special__test123"
        self.assertTrue(expected_folder.exists())
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    @patch('builtins.print')
    def test_download_video_extract_info_error(self, mock_print, mock_yt_dlp):
        """Test handling of extract_info error"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.side_effect = Exception("Network error")
        
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify error message was printed
        mock_print.assert_called_with("Error extracting video info: Network error")
        
        # Verify download was not attempted
        mock_ydl_instance.download.assert_not_called()
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    @patch('builtins.print')
    def test_download_video_download_error(self, mock_print, mock_yt_dlp):
        """Test handling of download error"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = self.mock_video_info
        mock_ydl_instance.download.side_effect = Exception("Download failed")
        
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify error message was printed
        mock_print.assert_called_with("Error downloading video: Download failed")
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_video_creates_output_directory(self, mock_yt_dlp):
        """Test that output directory is created if it doesn't exist"""
        non_existent_dir = os.path.join(self.temp_dir, "new_folder")
        self.assertFalse(os.path.exists(non_existent_dir))
        
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = self.mock_video_info
        mock_ydl_instance.download.return_value = None
        
        download_youtube_video(self.test_url, non_existent_dir)
        
        # Verify that the output directory was created
        self.assertTrue(os.path.exists(non_existent_dir))
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_download_video_default_output_dir(self, mock_yt_dlp):
        """Test that default output directory is used when not specified"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = self.mock_video_info
        mock_ydl_instance.download.return_value = None
        
        # Change to temp directory to avoid creating download-data in current dir
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            download_youtube_video(self.test_url)
            
            # Verify that default directory was created
            expected_dir = Path(self.temp_dir) / "download-data"
            self.assertTrue(expected_dir.exists())
        finally:
            os.chdir(original_cwd)
    
    @patch('youtube_downloader.yt_dlp.YoutubeDL')
    def test_yt_dlp_options_configuration(self, mock_yt_dlp):
        """Test that yt-dlp is configured with correct options"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = self.mock_video_info
        mock_ydl_instance.download.return_value = None
        
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Get the second call (download call) options
        download_call_args = mock_yt_dlp.call_args_list[1][0][0]
        
        # Verify key options are set correctly
        self.assertEqual(download_call_args['format'], 'best')
        self.assertTrue(download_call_args['writesubtitles'])
        self.assertTrue(download_call_args['writeautomaticsub'])
        self.assertEqual(download_call_args['subtitleslangs'], ['en', 'en-US'])
        self.assertEqual(download_call_args['subtitlesformat'], 'vtt')
        
        # Verify output template includes the video folder
        expected_folder = Path(self.temp_dir) / "Test Video Title_test123"
        self.assertIn(str(expected_folder), download_call_args['outtmpl'])


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)