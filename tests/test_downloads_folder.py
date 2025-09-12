#!/usr/bin/env python3
"""Tests for Downloads folder detection functionality"""

import unittest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import get_default_downloads_folder


class TestDownloadsFolderDetection(unittest.TestCase):
    """Test cross-platform Downloads folder detection"""

    @patch('config.settings.platform.system')
    @patch('config.settings.os.environ.get')
    def test_windows_downloads_folder_with_userprofile(self, mock_env_get, mock_platform):
        """Test Windows Downloads folder detection with USERPROFILE set"""
        # Mock Windows system
        mock_platform.return_value = "Windows"
        mock_env_get.return_value = "C:\\Users\\TestUser"
        
        result = get_default_downloads_folder()
        expected = str(Path("C:\\Users\\TestUser") / "Downloads" / "youtube-downloader")
        
        self.assertEqual(result, expected)
        mock_env_get.assert_called_once_with('USERPROFILE')

    @patch('config.settings.platform.system')
    @patch('config.settings.os.environ.get')
    @patch('config.settings.Path.cwd')
    def test_windows_downloads_folder_without_userprofile(self, mock_cwd, mock_env_get, mock_platform):
        """Test Windows Downloads folder detection fallback when USERPROFILE not set"""
        # Mock Windows system without USERPROFILE
        mock_platform.return_value = "Windows"
        mock_env_get.return_value = None
        mock_cwd.return_value = Path("C:\\CurrentDir")
        
        result = get_default_downloads_folder()
        expected = str(Path("C:\\CurrentDir") / "download-data" / "youtube-downloader")
        
        self.assertEqual(result, expected)
        mock_env_get.assert_called_once_with('USERPROFILE')

    @patch('config.settings.platform.system')
    @patch('config.settings.Path.home')
    def test_macos_downloads_folder(self, mock_home, mock_platform):
        """Test macOS Downloads folder detection"""
        # Mock macOS system
        mock_platform.return_value = "Darwin"
        mock_home.return_value = Path("/Users/testuser")
        
        result = get_default_downloads_folder()
        expected = str(Path("/Users/testuser") / "Downloads" / "youtube-downloader")
        
        self.assertEqual(result, expected)
        mock_home.assert_called_once()

    @patch('config.settings.platform.system')
    @patch('config.settings.Path.home')
    def test_linux_downloads_folder(self, mock_home, mock_platform):
        """Test Linux Downloads folder detection"""
        # Mock Linux system
        mock_platform.return_value = "Linux"
        mock_home.return_value = Path("/home/testuser")
        
        result = get_default_downloads_folder()
        expected = str(Path("/home/testuser") / "Downloads" / "youtube-downloader")
        
        self.assertEqual(result, expected)
        mock_home.assert_called_once()

    @patch('config.settings.platform.system')
    @patch('config.settings.Path.cwd')
    def test_unknown_system_fallback(self, mock_cwd, mock_platform):
        """Test unknown system fallback to current directory"""
        # Mock unknown system
        mock_platform.return_value = "FreeBSD"
        mock_cwd.return_value = Path("/unknown/path")
        
        result = get_default_downloads_folder()
        expected = str(Path("/unknown/path") / "download-data" / "youtube-downloader")
        
        self.assertEqual(result, expected)
        mock_cwd.assert_called_once()

    @patch('config.settings.platform.system')
    def test_case_insensitive_platform_detection(self, mock_platform):
        """Test that platform detection is case insensitive"""
        # Test various case combinations
        test_cases = [
            ("WINDOWS", "windows"),
            ("Windows", "windows"), 
            ("DARWIN", "darwin"),
            ("Darwin", "darwin"),
            ("LINUX", "linux"),
            ("Linux", "linux")
        ]
        
        for platform_name, expected_lower in test_cases:
            with self.subTest(platform=platform_name):
                mock_platform.return_value = platform_name
                # We don't need to test the full path logic again,
                # just that the platform.system().lower() call works
                with patch('config.settings.Path.home') as mock_home:
                    mock_home.return_value = Path("/test")
                    if expected_lower not in ["windows"]:
                        # For non-Windows systems, home() should be called
                        get_default_downloads_folder()
                        if expected_lower in ["darwin", "linux"]:
                            mock_home.assert_called()

    @patch('config.settings.platform.system')
    @patch('config.settings.os.environ.get')
    def test_windows_with_different_userprofile_formats(self, mock_env_get, mock_platform):
        """Test Windows Downloads folder with different USERPROFILE formats"""
        mock_platform.return_value = "Windows"
        
        # Test different Windows path formats
        test_paths = [
            "C:\\Users\\TestUser",
            "C:/Users/TestUser",  # Forward slashes (sometimes used)
            "D:\\Users\\AnotherUser"
        ]
        
        for user_path in test_paths:
            with self.subTest(userprofile=user_path):
                mock_env_get.return_value = user_path
                result = get_default_downloads_folder()
                expected = str(Path(user_path) / "Downloads" / "youtube-downloader")
                self.assertEqual(result, expected)

    def test_function_returns_string(self):
        """Test that the function always returns a string, not Path object"""
        result = get_default_downloads_folder()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    @patch('config.settings.platform.system')
    @patch('config.settings.Path.home')
    def test_subdirectory_creation_logic(self, mock_home, mock_platform):
        """Test that youtube-downloader subdirectory is always added"""
        mock_platform.return_value = "Darwin"
        mock_home.return_value = Path("/Users/testuser")
        
        result = get_default_downloads_folder()
        
        # Should always end with youtube-downloader
        self.assertTrue(result.endswith("youtube-downloader"))
        # Should contain Downloads folder
        self.assertIn("Downloads", result)


class TestDefaultOutputDirIntegration(unittest.TestCase):
    """Test integration of get_default_downloads_folder with DEFAULT_OUTPUT_DIR"""

    def test_default_output_dir_is_string(self):
        """Test that DEFAULT_OUTPUT_DIR is a string"""
        from config.settings import DEFAULT_OUTPUT_DIR
        self.assertIsInstance(DEFAULT_OUTPUT_DIR, str)
        self.assertTrue(len(DEFAULT_OUTPUT_DIR) > 0)

    def test_default_output_dir_contains_youtube_downloader(self):
        """Test that DEFAULT_OUTPUT_DIR contains our app subdirectory"""
        from config.settings import DEFAULT_OUTPUT_DIR
        self.assertTrue(DEFAULT_OUTPUT_DIR.endswith("youtube-downloader"))

    def test_default_output_dir_uses_function(self):
        """Test that DEFAULT_OUTPUT_DIR uses get_default_downloads_folder result"""
        # This test verifies the integration by checking the actual result
        from config.settings import DEFAULT_OUTPUT_DIR, get_default_downloads_folder
        
        # Call function directly and compare with DEFAULT_OUTPUT_DIR
        expected_result = get_default_downloads_folder()
        self.assertEqual(DEFAULT_OUTPUT_DIR, expected_result)


if __name__ == '__main__':
    unittest.main()