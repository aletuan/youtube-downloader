#!/usr/bin/env python3
"""Unit tests for UI factory functions"""

import unittest
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from gui.ui_factory import (
    create_header_section,
    create_input_section,
    create_button_section,
    create_status_section,
    create_video_info_card,
    create_config_section,
    create_theme_button,
    create_footer,
    create_main_card,
    get_common_folders
)


class TestUIFactory(unittest.TestCase):
    """Test cases for UI factory functions"""
    
    def test_create_header_section(self):
        """Test header section creation"""
        title, subtitle = create_header_section()
        
        # Test title properties - title is now a Row containing an Icon and Text
        self.assertEqual(len(title.controls), 2)  # Icon + Text
        self.assertIsInstance(title.controls[0], type(title.controls[0]))  # First is Icon
        self.assertEqual(title.controls[1].value, "YouTube Downloader")  # Text component
        self.assertEqual(title.controls[1].size, 32)  # Text size
        
        # Test subtitle properties
        self.assertEqual(subtitle.value, "Download YouTube videos with subtitles")
        self.assertEqual(subtitle.size, 16)
    
    def test_create_input_section(self):
        """Test input section creation"""
        url_input, output_dir_input, browse_button, dir_row = create_input_section()
        
        # Test URL input
        self.assertEqual(url_input.label, "YouTube URL")
        self.assertEqual(url_input.width, 600)
        
        # Test output directory input
        self.assertEqual(output_dir_input.label, "Output Directory")
        self.assertEqual(output_dir_input.width, 560)
        
        # Test browse button
        self.assertEqual(browse_button.tooltip, "Browse for folder")
        
        # Test dir row has correct components (Container wrapping a Row)
        self.assertEqual(len(dir_row.content.controls), 2)
        self.assertEqual(dir_row.content.controls[0], output_dir_input)
        self.assertEqual(dir_row.content.controls[1], browse_button)
    
    def test_create_button_section(self):
        """Test button section creation"""
        preview_button, download_button, play_button, button_row = create_button_section()
        
        # Test preview button
        self.assertEqual(preview_button.text, "Preview")
        self.assertEqual(preview_button.width, 140)
        
        # Test download button
        self.assertEqual(download_button.text, "Download")
        self.assertEqual(download_button.width, 140)
        self.assertTrue(download_button.disabled)  # Should be initially disabled
        
        # Test play button
        self.assertEqual(play_button.text, "Play")
        self.assertEqual(play_button.width, 140)
        self.assertFalse(play_button.visible)  # Should be initially hidden
        
        # Test button row has correct components
        self.assertEqual(len(button_row.controls), 3)
    
    def test_create_status_section(self):
        """Test status section creation"""
        status_text, progress_bar, progress_info = create_status_section()
        
        # Test status text
        self.assertEqual(status_text.value, "Ready to download")
        self.assertEqual(status_text.size, 14)
        
        # Test progress bar
        self.assertEqual(progress_bar.width, 580)
        self.assertFalse(progress_bar.visible)  # Should be initially hidden
        
        # Test progress info
        self.assertEqual(progress_info.value, "")
        self.assertEqual(progress_info.size, 11)
        self.assertFalse(progress_info.visible)  # Should be initially hidden
    
    def test_create_video_info_card(self):
        """Test video info card creation"""
        video_info_card = create_video_info_card()
        
        # Test card properties
        self.assertFalse(video_info_card.visible)  # Should be initially hidden
        self.assertEqual(video_info_card.elevation, 1)
        
        # Test card content structure
        info_column = video_info_card.content.content
        self.assertEqual(len(info_column.controls), 5)  # Title + 4 info fields
        self.assertEqual(info_column.controls[0].value, "Video Information")
    
    def test_create_config_section(self):
        """Test config section creation"""
        config_info = create_config_section()
        
        # Test config section structure
        column = config_info.content
        self.assertEqual(len(column.controls), 3)  # Title + Settings line + Translation line
        self.assertEqual(column.controls[0].value, "Settings")
    
    def test_create_theme_button(self):
        """Test theme button creation"""
        theme_button = create_theme_button()
        
        self.assertEqual(theme_button.tooltip, "Toggle Dark/Light Mode")
    
    def test_create_footer(self):
        """Test footer creation"""
        footer = create_footer()
        
        self.assertTrue("YouTube Downloader" in footer.value)
        self.assertTrue("Love" in footer.value)
        self.assertEqual(footer.size, 12)
    
    def test_create_main_card(self):
        """Test main card creation with components"""
        # Create some test components
        components = ["test1", "test2", "test3"]
        
        main_card = create_main_card(components)
        
        # Test card properties
        self.assertEqual(main_card.elevation, 4)
        
        # Test card content
        column = main_card.content.content
        self.assertEqual(len(column.controls), 3)
        self.assertEqual(column.controls, components)
    
    def test_get_common_folders(self):
        """Test common folders helper"""
        folders = get_common_folders()
        
        # Test that it returns a dictionary with expected keys
        expected_keys = {"Desktop", "Documents", "Downloads", "Movies", "Home"}
        self.assertEqual(set(folders.keys()), expected_keys)
        
        # Test that all paths are strings
        for path in folders.values():
            self.assertIsInstance(path, str)
            self.assertTrue(len(path) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)