#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.downloader import (
    download_youtube_video,
    _get_video_info,
    _create_video_folder,
    _get_yt_dlp_options,
    _check_video_exists
)


class TestGetVideoInfo(unittest.TestCase):
    """Test cases for the _get_video_info function"""
    
    @patch('core.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_yt_dlp):
        """Test successful video info extraction"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'title': 'Test Video Title',
            'id': 'test123'
        }
        
        title, video_id = _get_video_info('https://youtube.com/watch?v=test123')
        
        self.assertEqual(title, 'Test Video Title')
        self.assertEqual(video_id, 'test123')
        mock_ydl_instance.extract_info.assert_called_once_with('https://youtube.com/watch?v=test123', download=False)
    
    @patch('core.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_with_invalid_chars(self, mock_yt_dlp):
        """Test video info extraction with title containing invalid characters"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'title': 'Test Video: Part <1> | "Special"',
            'id': 'test123'
        }
        
        title, video_id = _get_video_info('https://youtube.com/watch?v=test123')
        
        self.assertEqual(title, 'Test Video_ Part _1_ _ _Special_')
        self.assertEqual(video_id, 'test123')
    
    @patch('core.downloader.yt_dlp.YoutubeDL')
    def test_get_video_info_missing_title(self, mock_yt_dlp):
        """Test video info extraction when title is missing"""
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = {
            'id': 'test123'
        }
        
        title, video_id = _get_video_info('https://youtube.com/watch?v=test123')
        
        self.assertEqual(title, 'Unknown')
        self.assertEqual(video_id, 'test123')


class TestCreateVideoFolder(unittest.TestCase):
    """Test cases for the _create_video_folder function"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_video_folder_success(self):
        """Test successful video folder creation"""
        video_folder = _create_video_folder(self.temp_dir, "Test Video", "test123")
        
        expected_folder = Path(self.temp_dir) / "Test Video_test123"
        self.assertEqual(video_folder, expected_folder)
        self.assertTrue(video_folder.exists())
        self.assertTrue(video_folder.is_dir())
    
    def test_create_video_folder_output_dir_not_exists(self):
        """Test video folder creation when output directory doesn't exist"""
        non_existent_dir = os.path.join(self.temp_dir, "new_folder")
        
        video_folder = _create_video_folder(non_existent_dir, "Test Video", "test123")
        
        self.assertTrue(Path(non_existent_dir).exists())
        self.assertTrue(video_folder.exists())
    
    def test_create_video_folder_already_exists(self):
        """Test video folder creation when folder already exists"""
        # Create the folder first
        existing_folder = Path(self.temp_dir) / "Test Video_test123"
        existing_folder.mkdir(parents=True)
        
        video_folder = _create_video_folder(self.temp_dir, "Test Video", "test123")
        
        self.assertEqual(video_folder, existing_folder)
        self.assertTrue(video_folder.exists())


class TestGetYtDlpOptions(unittest.TestCase):
    """Test cases for the _get_yt_dlp_options function"""
    
    def test_get_yt_dlp_options_structure(self):
        """Test that yt-dlp options are configured correctly"""
        video_folder = Path("/test/folder")
        options = _get_yt_dlp_options(video_folder)
        
        # Test core required options (ignore anti-bot headers for test)
        required_options = {
            'outtmpl': str(video_folder / '%(title)s.%(ext)s'),
            'format': 'best',
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US'],
            'subtitlesformat': 'vtt',
        }
        
        # Check that all required options are present
        for key, value in required_options.items():
            self.assertIn(key, options)
            self.assertEqual(options[key], value)
        
        # Check that anti-bot headers are present
        self.assertIn('http_headers', options)
        self.assertIn('User-Agent', options['http_headers'])
    
    def test_get_yt_dlp_options_output_template(self):
        """Test that output template is correctly formatted"""
        video_folder = Path("/test/My Video_test123")
        options = _get_yt_dlp_options(video_folder)
        
        expected_template = "/test/My Video_test123/%(title)s.%(ext)s"
        self.assertEqual(options['outtmpl'], expected_template)


class TestCheckVideoExists(unittest.TestCase):
    """Test cases for the _check_video_exists function"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_check_video_not_exists(self):
        """Test checking for non-existent video"""
        exists, video_folder, files = _check_video_exists(self.temp_dir, "Test Video", "test123")
        
        self.assertFalse(exists)
        self.assertEqual(video_folder.name, "Test Video_test123")
        self.assertEqual(files, [])
    
    def test_check_video_folder_exists_no_video_files(self):
        """Test checking when folder exists but no video files"""
        # Create folder but no video files
        video_folder = Path(self.temp_dir) / "Test Video_test123"
        video_folder.mkdir(parents=True)
        
        # Create some non-video files
        (video_folder / "subtitles.vtt").touch()
        (video_folder / "info.json").touch()
        
        exists, returned_folder, files = _check_video_exists(self.temp_dir, "Test Video", "test123")
        
        self.assertFalse(exists)
        self.assertEqual(returned_folder, video_folder)
        self.assertEqual(files, [])
    
    def test_check_video_exists_with_video_files(self):
        """Test checking when video files exist"""
        # Create folder and video files
        video_folder = Path(self.temp_dir) / "Test Video_test123"
        video_folder.mkdir(parents=True)
        
        # Create video files
        (video_folder / "test_video.mp4").touch()
        (video_folder / "subtitles.vtt").touch()
        
        exists, returned_folder, files = _check_video_exists(self.temp_dir, "Test Video", "test123")
        
        self.assertTrue(exists)
        self.assertEqual(returned_folder, video_folder)
        self.assertIn("test_video.mp4", files)
        self.assertEqual(len(files), 1)  # Only video files, not subtitles
    
    def test_check_video_exists_multiple_video_files(self):
        """Test checking with multiple video files"""
        # Create folder and multiple video files
        video_folder = Path(self.temp_dir) / "Test Video_test123"
        video_folder.mkdir(parents=True)
        
        # Create multiple video files
        (video_folder / "video.mp4").touch()
        (video_folder / "video.mkv").touch()
        (video_folder / "audio.m4a").touch()  # This shouldn't be counted as video
        
        exists, returned_folder, files = _check_video_exists(self.temp_dir, "Test Video", "test123")
        
        self.assertTrue(exists)
        self.assertEqual(len(files), 2)  # Only .mp4 and .mkv
        self.assertIn("video.mp4", files)
        self.assertIn("video.mkv", files)
        self.assertNotIn("audio.m4a", files)
    
    def test_check_video_exists_case_insensitive_extensions(self):
        """Test that video extension checking is case insensitive"""
        # Create folder and video files with different cases
        video_folder = Path(self.temp_dir) / "Test Video_test123"
        video_folder.mkdir(parents=True)
        
        # Create video files with different case extensions
        (video_folder / "video.MP4").touch()
        (video_folder / "video.MKV").touch()
        
        exists, returned_folder, files = _check_video_exists(self.temp_dir, "Test Video", "test123")
        
        self.assertTrue(exists)
        self.assertEqual(len(files), 2)
        self.assertIn("video.MP4", files)
        self.assertIn("video.MKV", files)


class TestDownloadYoutubeVideo(unittest.TestCase):
    """Test cases for the download_youtube_video function"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://www.youtube.com/watch?v=test123"
    
    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('core.downloader._get_video_info')
    @patch('core.downloader.yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_yt_dlp, mock_get_video_info):
        """Test successful video download"""
        # Mock the helper functions
        mock_get_video_info.return_value = ("Test Video Title", "test123")
        
        # Mock the YoutubeDL context manager for download
        mock_ydl_instance = MagicMock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.download.return_value = None
        
        # Call the function
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify that helper functions were called
        mock_get_video_info.assert_called_once_with(self.test_url)
        mock_ydl_instance.download.assert_called_once_with([self.test_url])
        
        # Verify that the video folder was created
        expected_folder = Path(self.temp_dir) / "Test Video Title_test123"
        self.assertTrue(expected_folder.exists())
    
    @patch('core.downloader._get_video_info')
    @patch('builtins.print')
    def test_download_video_extract_info_error(self, mock_print, mock_get_video_info):
        """Test handling of extract_info error"""
        mock_get_video_info.side_effect = Exception("Network error")
        
        download_youtube_video(self.test_url, self.temp_dir)
        
        # Verify error message was printed
        mock_print.assert_called_with("Error extracting video info: Network error")


if __name__ == '__main__':
    unittest.main(verbosity=2)