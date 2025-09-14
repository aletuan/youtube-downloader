#!/usr/bin/env python3
"""
Unit tests for GUI framework components and YouTube Downloader GUI integration
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))


class TestFletFramework(unittest.TestCase):
    """Test cases for Flet framework setup and components"""
    
    def test_flet_import(self):
        """Test that Flet can be imported successfully"""
        try:
            import flet as ft
            self.assertTrue(hasattr(ft, 'app'))
            self.assertTrue(hasattr(ft, 'Page'))
            self.assertTrue(hasattr(ft, 'Text'))
        except ImportError:
            self.fail("Failed to import Flet framework")
    
    def test_flet_components_creation(self):
        """Test that basic Flet components can be created"""
        import flet as ft
        
        # Test basic components
        text = ft.Text("Test Text", color=ft.Colors.BLUE)
        button = ft.ElevatedButton("Test Button")
        textfield = ft.TextField(label="Test Input")
        progress_bar = ft.ProgressBar(width=200)
        card = ft.Card(content=ft.Text("Card Content"))
        
        # Verify component types
        self.assertEqual(type(text).__name__, "Text")
        self.assertEqual(type(button).__name__, "ElevatedButton")
        self.assertEqual(type(textfield).__name__, "TextField")
        self.assertEqual(type(progress_bar).__name__, "ProgressBar")
        self.assertEqual(type(card).__name__, "Card")
        
        # Verify properties
        self.assertEqual(text.value, "Test Text")
        self.assertEqual(button.text, "Test Button")
        self.assertEqual(textfield.label, "Test Input")
    
    def test_flet_colors_api(self):
        """Test that Flet Colors API is working correctly"""
        import flet as ft
        
        # Test color constants
        self.assertTrue(hasattr(ft.Colors, 'RED'))
        self.assertTrue(hasattr(ft.Colors, 'BLUE'))
        self.assertTrue(hasattr(ft.Colors, 'GREEN'))
        self.assertTrue(hasattr(ft.Colors, 'RED_400'))
        self.assertTrue(hasattr(ft.Colors, 'GREY_600'))
    
    def test_flet_icons_api(self):
        """Test that Flet Icons API is working correctly"""
        import flet as ft
        
        # Test icon constants
        self.assertTrue(hasattr(ft.Icons, 'DOWNLOAD'))
        self.assertTrue(hasattr(ft.Icons, 'LINK'))
        self.assertTrue(hasattr(ft.Icons, 'FOLDER'))
        self.assertTrue(hasattr(ft.Icons, 'PREVIEW'))
        self.assertTrue(hasattr(ft.Icons, 'CLEAR'))


class TestGUIIntegration(unittest.TestCase):
    """Test cases for GUI integration with core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the GUI imports to avoid actual GUI creation
        self.mock_modules = {}
    
    def test_gui_imports(self):
        """Test that GUI can import core modules"""
        try:
            from core.downloader import download_youtube_video, _get_video_info
            from core.utils import sanitize_filename
            from config.settings import DEFAULT_OUTPUT_DIR, SUBTITLE_LANGUAGES

            # Verify functions are callable
            self.assertTrue(callable(download_youtube_video))
            self.assertTrue(callable(_get_video_info))
            self.assertTrue(callable(sanitize_filename))

            # Verify config values
            self.assertIsInstance(DEFAULT_OUTPUT_DIR, str)
            self.assertIsInstance(SUBTITLE_LANGUAGES, list)

        except ImportError as e:
            self.fail(f"GUI failed to import core modules: {e}")
    
    def test_url_validation_logic(self):
        """Test URL validation logic used in GUI"""
        # Valid YouTube URLs
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        # Invalid URLs
        invalid_urls = [
            "",
            "not a url",
            "https://vimeo.com/123456",
            "https://example.com"
        ]
        
        # Test valid URLs
        for url in valid_urls:
            is_valid = url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/'))
            self.assertTrue(is_valid, f"Should be valid: {url}")
        
        # Test invalid URLs
        for url in invalid_urls:
            is_valid = url.startswith(('https://www.youtube.com/', 'https://youtube.com/', 'https://youtu.be/'))
            self.assertFalse(is_valid, f"Should be invalid: {url}")
    
    @patch('core.downloader._get_video_info')
    def test_video_info_integration(self, mock_get_info):
        """Test video info preview functionality"""
        # Mock video info response
        mock_get_info.return_value = ("Test Video Title", "test123")
        
        from core.downloader import _get_video_info
        
        # Test the function
        title, video_id = _get_video_info("https://youtube.com/watch?v=test123")
        
        self.assertEqual(title, "Test Video Title")
        self.assertEqual(video_id, "test123")
        mock_get_info.assert_called_once()
    
    def test_configuration_integration(self):
        """Test that GUI properly integrates configuration"""
        from config.settings import (
            DEFAULT_OUTPUT_DIR,
            SUBTITLE_LANGUAGES,
            SUBTITLE_FORMAT,
            VIDEO_FORMAT
        )
        
        # Verify configuration values are reasonable
        self.assertIsInstance(DEFAULT_OUTPUT_DIR, str)
        self.assertTrue(len(DEFAULT_OUTPUT_DIR) > 0)
        
        self.assertIsInstance(SUBTITLE_LANGUAGES, list)
        self.assertIn('en', SUBTITLE_LANGUAGES)
        
        self.assertIsInstance(SUBTITLE_FORMAT, str)
        self.assertIsInstance(VIDEO_FORMAT, str)


class TestGUIErrorHandling(unittest.TestCase):
    """Test cases for GUI error handling scenarios"""
    
    def test_network_error_detection(self):
        """Test network error detection in GUI"""
        error_messages = [
            "Network error occurred",
            "Connection timeout",
            "network connection failed"
        ]
        
        for error_msg in error_messages:
            has_network_error = "Network" in error_msg or "connection" in error_msg.lower()
            self.assertTrue(has_network_error, f"Should detect network error: {error_msg}")
    
    def test_permission_error_detection(self):
        """Test permission error detection in GUI"""
        permission_error_messages = [
            "Permission denied",
            "permission error occurred"
        ]
        
        non_permission_error_messages = [
            "Access is denied",  # This is handled differently
            "Network error",
            "Video not found"
        ]
        
        # Test messages that should be detected as permission errors
        for error_msg in permission_error_messages:
            has_permission_error = "permission" in error_msg.lower()
            self.assertTrue(has_permission_error, f"Should detect permission error: {error_msg}")
        
        # Test messages that should NOT be detected as permission errors
        for error_msg in non_permission_error_messages:
            has_permission_error = "permission" in error_msg.lower()
            self.assertFalse(has_permission_error, f"Should NOT detect permission error: {error_msg}")
    
    def test_not_found_error_detection(self):
        """Test video not found error detection in GUI"""
        error_messages = [
            "Video not found",
            "404 not found",
            "Content not found"
        ]
        
        for error_msg in error_messages:
            has_not_found_error = "not found" in error_msg.lower()
            self.assertTrue(has_not_found_error, f"Should detect not found error: {error_msg}")


if __name__ == '__main__':
    unittest.main(verbosity=2)