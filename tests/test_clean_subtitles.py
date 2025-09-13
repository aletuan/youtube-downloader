#!/usr/bin/env python3
"""Unit tests for clean_subtitles module"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.clean_subtitles import (
    clean_html_tags,
    clean_vietnamese_subtitle_file,
    clean_html_tags_only,
    clean_vietnamese_translation_artifacts,
    _has_translation_artifacts,
    _clean_vtt_block
)


class TestCleanHtmlTags(unittest.TestCase):
    """Test cases for HTML tag cleaning functionality"""
    
    def test_clean_timestamp_tags(self):
        """Test removal of timestamp tags like <00:03:09.360>"""
        text = "into<00:03:09.120><c> a</c><00:03:09.360><c> mathematical</c><00:03:09.920><c> format</c>"
        result = clean_html_tags(text)
        expected = "into a mathematical format"
        self.assertEqual(result, expected)
    
    def test_clean_common_html_tags(self):
        """Test removal of common HTML tags"""
        text = "<c>Hello</c> <i>world</i> <b>test</b>"
        result = clean_html_tags(text)
        expected = "Hello world test"
        self.assertEqual(result, expected)
    
    def test_clean_mixed_tags(self):
        """Test removal of mixed timestamp and HTML tags"""
        text = "<00:01:23.456>Text<00:01:24.789> with <c>mixed</c> content"
        result = clean_html_tags(text)
        expected = "Text with mixed content"
        self.assertEqual(result, expected)
    
    def test_clean_extra_spaces(self):
        """Test cleaning of extra spaces after tag removal"""
        text = "  <c>  Extra   spaces  </c>  "
        result = clean_html_tags(text)
        expected = "Extra spaces"
        self.assertEqual(result, expected)
    
    def test_no_tags_to_clean(self):
        """Test text without any tags"""
        text = "Normal text without tags"
        result = clean_html_tags(text)
        expected = "Normal text without tags"
        self.assertEqual(result, expected)
    
    def test_empty_text(self):
        """Test empty text input"""
        text = ""
        result = clean_html_tags(text)
        expected = ""
        self.assertEqual(result, expected)


class TestTranslationArtifacts(unittest.TestCase):
    """Test cases for Vietnamese translation artifact detection"""
    
    def test_has_translation_artifacts_positive(self):
        """Test detection of translation artifacts"""
        lines = ["This is normal text", "Sau đây là bản dịch", "More text"]
        has_artifacts, artifact_line = _has_translation_artifacts(lines)
        self.assertTrue(has_artifacts)
        self.assertIn("Sau đây", artifact_line)
    
    def test_has_translation_artifacts_ban_dich(self):
        """Test detection of 'bản dịch' artifact"""
        lines = ["Normal content", "Đây là bản dịch tiếng Việt"]
        has_artifacts, artifact_line = _has_translation_artifacts(lines)
        self.assertTrue(has_artifacts)
        self.assertIn("bản dịch", artifact_line)
    
    def test_has_translation_artifacts_phu_de(self):
        """Test detection of 'phụ đề' artifact"""
        lines = ["Good content", "Đây là phụ đề tự động"]
        has_artifacts, artifact_line = _has_translation_artifacts(lines)
        self.assertTrue(has_artifacts)
        self.assertIn("phụ đề", artifact_line)
    
    def test_has_translation_artifacts_negative(self):
        """Test clean text without artifacts"""
        lines = ["This is normal text", "No artifacts here", "Clean content"]
        has_artifacts, artifact_line = _has_translation_artifacts(lines)
        self.assertFalse(has_artifacts)
        self.assertIsNone(artifact_line)
    
    def test_has_translation_artifacts_case_insensitive(self):
        """Test case-insensitive artifact detection"""
        lines = ["Normal text", "SAU ĐÂY LÀ PHẦN DỊCH"]
        has_artifacts, artifact_line = _has_translation_artifacts(lines)
        self.assertTrue(has_artifacts)


class TestVttBlockCleaning(unittest.TestCase):
    """Test cases for VTT block cleaning functionality"""
    
    def test_clean_vtt_block_with_artifacts(self):
        """Test VTT block with translation artifacts should be removed"""
        lines = ["00:00:01.000 --> 00:00:05.000", "Sau đây là bản dịch"]
        should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts=True, remove_html_tags=True)
        self.assertFalse(should_keep)
        self.assertEqual(cleaned_lines, [])
    
    def test_clean_vtt_block_with_html_tags(self):
        """Test VTT block with HTML tags should be cleaned"""
        lines = ["00:00:01.000 --> 00:00:05.000", "Hello <c>world</c> test"]
        should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts=True, remove_html_tags=True)
        self.assertTrue(should_keep)
        self.assertEqual(len(cleaned_lines), 2)
        self.assertEqual(cleaned_lines[0], "00:00:01.000 --> 00:00:05.000")
        self.assertEqual(cleaned_lines[1], "Hello world test")
    
    def test_clean_vtt_block_preserve_timing(self):
        """Test that timing lines are preserved"""
        lines = ["00:00:01.000 --> 00:00:05.000", "Normal content"]
        should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts=True, remove_html_tags=True)
        self.assertTrue(should_keep)
        self.assertEqual(cleaned_lines[0], "00:00:01.000 --> 00:00:05.000")
    
    def test_clean_vtt_block_skip_artifacts_disabled(self):
        """Test VTT block with artifacts when artifact removal is disabled"""
        lines = ["00:00:01.000 --> 00:00:05.000", "Sau đây là bản dịch"]
        should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts=False, remove_html_tags=True)
        self.assertTrue(should_keep)
        self.assertEqual(len(cleaned_lines), 2)
    
    def test_clean_vtt_block_skip_html_cleaning(self):
        """Test VTT block with HTML tags when tag cleaning is disabled"""
        lines = ["00:00:01.000 --> 00:00:05.000", "Hello <c>world</c> test"]
        should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts=True, remove_html_tags=False)
        self.assertTrue(should_keep)
        self.assertEqual(cleaned_lines[1], "Hello <c>world</c> test")


class TestVttFileCleaning(unittest.TestCase):
    """Test cases for complete VTT file cleaning"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_clean_vietnamese_subtitle_file_complete(self):
        """Test complete cleaning of Vietnamese subtitle file"""
        test_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Hello <c>world</c> with tags

00:00:05.000 --> 00:00:10.000
Sau đây là bản dịch không mong muốn

00:00:10.000 --> 00:00:15.000
Good content with <i>more</i> <b>tags</b>

00:00:15.000 --> 00:00:20.000
Đây là phụ đề tự động

00:00:20.000 --> 00:00:25.000
Final good content
"""
        
        vtt_file = self.temp_path / "test.vi.vtt"
        with open(vtt_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Test the cleaning
        result = clean_vietnamese_subtitle_file(str(vtt_file))
        self.assertTrue(result)
        
        # Read and verify the result
        with open(vtt_file, 'r', encoding='utf-8') as f:
            cleaned_content = f.read()
        
        # Verify artifacts are removed
        self.assertNotIn("bản dịch", cleaned_content.lower())
        self.assertNotIn("phụ đề", cleaned_content.lower())
        
        # Verify HTML tags are removed
        self.assertNotIn("<c>", cleaned_content)
        self.assertNotIn("<i>", cleaned_content)
        self.assertNotIn("<b>", cleaned_content)
        
        # Verify good content is preserved
        self.assertIn("Hello world with tags", cleaned_content)
        self.assertIn("Good content with more tags", cleaned_content)
        self.assertIn("Final good content", cleaned_content)
        
        # Verify VTT structure is preserved
        self.assertIn("WEBVTT", cleaned_content)
        self.assertIn("00:00:01.000 --> 00:00:05.000", cleaned_content)
    
    def test_clean_html_tags_only_function(self):
        """Test HTML tag cleaning without artifact removal"""
        test_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Hello <c>world</c> test

00:00:05.000 --> 00:00:10.000
Sau đây là bản dịch (should be kept)

00:00:10.000 --> 00:00:15.000
Content with <i>tags</i> only
"""
        
        vtt_file = self.temp_path / "test.vi.vtt"
        with open(vtt_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Test HTML tag cleaning only
        result = clean_html_tags_only(str(vtt_file))
        self.assertTrue(result)
        
        # Read and verify the result
        with open(vtt_file, 'r', encoding='utf-8') as f:
            cleaned_content = f.read()
        
        # Verify HTML tags are removed
        self.assertNotIn("<c>", cleaned_content)
        self.assertNotIn("<i>", cleaned_content)
        
        # Verify artifacts are kept (not removed)
        self.assertIn("Sau đây là bản dịch", cleaned_content)
        
        # Verify content with tags cleaned
        self.assertIn("Hello world test", cleaned_content)
        self.assertIn("Content with tags only", cleaned_content)
    
    def test_clean_vietnamese_translation_artifacts_function(self):
        """Test the main cleaning function used by translation module"""
        test_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Good content <c>with</c> tags

00:00:05.000 --> 00:00:10.000
Đây là bản dịch tự động
"""
        
        vtt_file = self.temp_path / "test.vi.vtt"
        with open(vtt_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Test the main cleaning function
        result = clean_vietnamese_translation_artifacts(vtt_file)
        self.assertTrue(result)
        
        # Read and verify the result
        with open(vtt_file, 'r', encoding='utf-8') as f:
            cleaned_content = f.read()
        
        # Should remove both artifacts and HTML tags
        self.assertNotIn("bản dịch", cleaned_content.lower())
        self.assertNotIn("<c>", cleaned_content)
        self.assertIn("Good content with tags", cleaned_content)
    
    def test_clean_file_not_found(self):
        """Test cleaning non-existent file"""
        non_existent_file = self.temp_path / "not_found.vtt"
        result = clean_vietnamese_subtitle_file(str(non_existent_file))
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)