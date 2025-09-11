#!/usr/bin/env python3
"""Unit tests for validation utilities"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.validation import (
    validate_youtube_url,
    validate_output_directory,
    classify_error_type,
    is_network_error,
    is_permission_error,
    is_not_found_error
)


class TestValidateYoutubeUrl(unittest.TestCase):
    """Test cases for YouTube URL validation"""
    
    def test_valid_youtube_urls(self):
        """Test valid YouTube URL formats"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            is_valid, error = validate_youtube_url(url)
            self.assertTrue(is_valid, f"Should be valid: {url}")
            self.assertIsNone(error, f"Should have no error: {url}")
    
    def test_invalid_youtube_urls(self):
        """Test invalid YouTube URL formats"""
        invalid_urls = [
            "",
            "   ",
            "not a url",
            "https://vimeo.com/123456",
            "https://example.com",
            "http://youtube.com/watch?v=test"  # http instead of https
        ]
        
        for url in invalid_urls:
            is_valid, error = validate_youtube_url(url)
            self.assertFalse(is_valid, f"Should be invalid: {url}")
            self.assertIsNotNone(error, f"Should have error message: {url}")
    
    def test_empty_url_error_message(self):
        """Test error message for empty URL"""
        is_valid, error = validate_youtube_url("")
        self.assertFalse(is_valid)
        self.assertEqual(error, "Please enter a YouTube URL")
    
    def test_invalid_url_error_message(self):
        """Test error message for invalid URL"""
        is_valid, error = validate_youtube_url("https://example.com")
        self.assertFalse(is_valid)
        self.assertEqual(error, "Please enter a valid YouTube URL")


class TestValidateOutputDirectory(unittest.TestCase):
    """Test cases for output directory validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_valid_existing_directory(self):
        """Test validation of existing directory"""
        is_valid, error = validate_output_directory(self.temp_dir)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_create_new_directory(self):
        """Test creation of new directory"""
        new_dir = os.path.join(self.temp_dir, "new_folder")
        is_valid, error = validate_output_directory(new_dir)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertTrue(os.path.exists(new_dir))
    
    def test_empty_directory_path(self):
        """Test empty directory path"""
        is_valid, error = validate_output_directory("")
        self.assertFalse(is_valid)
        self.assertEqual(error, "Please specify an output directory")
    
    def test_whitespace_directory_path(self):
        """Test whitespace-only directory path"""
        is_valid, error = validate_output_directory("   ")
        self.assertFalse(is_valid)
        self.assertEqual(error, "Please specify an output directory")


class TestClassifyErrorType(unittest.TestCase):
    """Test cases for error classification"""
    
    def test_network_errors(self):
        """Test network error classification"""
        network_errors = [
            "Network error occurred",
            "Connection timeout",
            "network connection failed"
        ]
        
        for error in network_errors:
            result = classify_error_type(error)
            self.assertTrue(result.startswith("❌ Network error"))
    
    def test_permission_errors(self):
        """Test permission error classification"""
        permission_errors = [
            "Permission denied",
            "permission error occurred"
        ]
        
        for error in permission_errors:
            result = classify_error_type(error)
            self.assertTrue(result.startswith("❌ Permission error"))
    
    def test_not_found_errors(self):
        """Test not found error classification"""
        not_found_errors = [
            "Video not found",
            "404 not found",
            "Content not found"
        ]
        
        for error in not_found_errors:
            result = classify_error_type(error)
            self.assertTrue(result.startswith("❌ Video not found"))
    
    def test_rate_limit_errors(self):
        """Test rate limit error classification"""
        rate_limit_errors = [
            "HTTP Error 429: Too Many Requests",
            "too many requests made"
        ]
        
        for error in rate_limit_errors:
            result = classify_error_type(error)
            self.assertTrue(result.startswith("❌ Rate limited"))
    
    def test_generic_errors(self):
        """Test generic error classification"""
        generic_error = "Some unknown error"
        result = classify_error_type(generic_error)
        self.assertEqual(result, "❌ Error: Some unknown error")


class TestErrorDetectionHelpers(unittest.TestCase):
    """Test cases for error detection helper functions"""
    
    def test_is_network_error(self):
        """Test network error detection"""
        self.assertTrue(is_network_error("Network error occurred"))
        self.assertTrue(is_network_error("connection timeout"))
        self.assertFalse(is_network_error("Permission denied"))
    
    def test_is_permission_error(self):
        """Test permission error detection"""
        self.assertTrue(is_permission_error("Permission denied"))
        self.assertTrue(is_permission_error("permission error"))
        self.assertFalse(is_permission_error("Network error"))
    
    def test_is_not_found_error(self):
        """Test not found error detection"""
        self.assertTrue(is_not_found_error("Video not found"))
        self.assertTrue(is_not_found_error("404 Not Found"))
        self.assertFalse(is_not_found_error("Permission denied"))


if __name__ == '__main__':
    unittest.main(verbosity=2)