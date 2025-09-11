#!/usr/bin/env python3
import unittest
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.utils import sanitize_filename


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


if __name__ == '__main__':
    unittest.main(verbosity=2)