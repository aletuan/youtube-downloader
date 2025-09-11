#!/usr/bin/env python3
"""Unit tests for translation module"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# Mock anthropic module before importing translation
sys.modules['anthropic'] = MagicMock()

from core.translation import (
    SubtitleTranslator,
    VTTEntry, 
    translate_subtitle_files
)


class TestVTTEntry(unittest.TestCase):
    """Test cases for VTTEntry data class"""
    
    def test_vtt_entry_creation(self):
        """Test VTTEntry creation with all fields"""
        entry = VTTEntry(
            index=1,
            start_time="00:00:01.000",
            end_time="00:00:03.000",
            text="Hello world",
            original_line="1\n00:00:01.000 --> 00:00:03.000\nHello world"
        )
        
        self.assertEqual(entry.index, 1)
        self.assertEqual(entry.start_time, "00:00:01.000")
        self.assertEqual(entry.end_time, "00:00:03.000")
        self.assertEqual(entry.text, "Hello world")
        self.assertIn("Hello world", entry.original_line)


class TestSubtitleTranslator(unittest.TestCase):
    """Test cases for SubtitleTranslator class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Sample VTT content for testing
        self.sample_vtt_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
Hello, this is the first subtitle.

00:00:04.000 --> 00:00:06.000
This is the second subtitle line.

00:00:07.000 --> 00:00:09.000
And this is the third one.
"""
        
        # Create sample VTT file
        self.vtt_file = self.temp_path / "test_video.en.vtt"
        with open(self.vtt_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_vtt_content)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_translator_initialization_no_key(self):
        """Test translator initialization without API key"""
        translator = SubtitleTranslator()
        self.assertIsNone(translator.api_key)
        self.assertIsNone(translator.client)
    
    def test_translator_initialization_with_key(self):
        """Test translator initialization with API key"""
        with patch('core.translation.anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client
            
            translator = SubtitleTranslator(api_key="test-key")
            self.assertEqual(translator.api_key, "test-key")
            self.assertEqual(translator.client, mock_client)
            mock_anthropic.Anthropic.assert_called_once_with(api_key="test-key")
    
    def test_parse_vtt_file(self):
        """Test VTT file parsing"""
        translator = SubtitleTranslator()
        entries = translator._parse_vtt_file(self.vtt_file)
        
        self.assertEqual(len(entries), 3)
        
        # Check first entry
        self.assertEqual(entries[0].start_time, "00:00:01.000")
        self.assertEqual(entries[0].end_time, "00:00:03.000")
        self.assertEqual(entries[0].text, "Hello, this is the first subtitle.")
        
        # Check second entry
        self.assertEqual(entries[1].start_time, "00:00:04.000")
        self.assertEqual(entries[1].end_time, "00:00:06.000")
        self.assertEqual(entries[1].text, "This is the second subtitle line.")
        
        # Check third entry
        self.assertEqual(entries[2].start_time, "00:00:07.000")
        self.assertEqual(entries[2].end_time, "00:00:09.000")
        self.assertEqual(entries[2].text, "And this is the third one.")
    
    def test_parse_vtt_file_not_found(self):
        """Test parsing non-existent VTT file"""
        translator = SubtitleTranslator()
        non_existent_file = self.temp_path / "not_found.vtt"
        
        with self.assertRaises(FileNotFoundError):
            translator._parse_vtt_file(non_existent_file)
    
    def test_get_language_code(self):
        """Test language code mapping"""
        translator = SubtitleTranslator()
        
        self.assertEqual(translator._get_language_code("Vietnamese"), "vi")
        self.assertEqual(translator._get_language_code("spanish"), "es")
        self.assertEqual(translator._get_language_code("French"), "fr")
        self.assertEqual(translator._get_language_code("Unknown"), "trans")
    
    @patch('core.translation.anthropic')
    def test_translate_batch_success(self, mock_anthropic):
        """Test successful batch translation"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Xin chào---SEPARATOR---Đây là dòng phụ đề thứ hai"
        mock_client.messages.create.return_value = mock_response
        
        translator = SubtitleTranslator(api_key="test-key")
        
        texts = ["Hello", "This is the second subtitle"]
        translated = translator._translate_batch(texts, "Vietnamese")
        
        self.assertEqual(len(translated), 2)
        self.assertEqual(translated[0], "Xin chào")
        self.assertEqual(translated[1], "Đây là dòng phụ đề thứ hai")
        
        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        self.assertEqual(call_args[1]['model'], 'claude-3-haiku-20240307')
        self.assertIn("Vietnamese", call_args[1]['messages'][0]['content'])
    
    @patch('core.translation.anthropic')
    def test_translate_batch_api_error(self, mock_anthropic):
        """Test batch translation with API error"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        translator = SubtitleTranslator(api_key="test-key")
        
        texts = ["Hello", "World"]
        translated = translator._translate_batch(texts, "Vietnamese")
        
        # Should return original texts on error
        self.assertEqual(translated, texts)
    
    @patch('core.translation.anthropic')
    def test_create_translated_vtt(self, mock_anthropic):
        """Test creation of translated VTT file"""
        # Setup translator
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        translator = SubtitleTranslator(api_key="test-key")
        
        # Parse original VTT
        entries = translator._parse_vtt_file(self.vtt_file)
        
        # Mock translated texts
        translated_texts = [
            "Xin chào, đây là phụ đề đầu tiên.",
            "Đây là dòng phụ đề thứ hai.",
            "Và đây là dòng thứ ba."
        ]
        
        # Create translated VTT
        translated_path = translator._create_translated_vtt(
            self.vtt_file, entries, translated_texts, "Vietnamese"
        )
        
        # Verify file was created
        self.assertTrue(translated_path.exists())
        self.assertEqual(translated_path.name, "test_video.vi.vtt")
        
        # Verify content
        with open(translated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("WEBVTT", content)
        self.assertIn("00:00:01.000 --> 00:00:03.000", content)
        self.assertIn("Xin chào, đây là phụ đề đầu tiên.", content)
        self.assertIn("Đây là dòng phụ đề thứ hai.", content)
        self.assertIn("Và đây là dòng thứ ba.", content)
    
    @patch('core.translation.anthropic')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_translate_vtt_file_success(self, mock_sleep, mock_anthropic):
        """Test successful VTT file translation end-to-end"""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Xin chào, đây là phụ đề đầu tiên.---SEPARATOR---Đây là dòng phụ đề thứ hai.---SEPARATOR---Và đây là dòng thứ ba."
        mock_client.messages.create.return_value = mock_response
        
        translator = SubtitleTranslator(api_key="test-key")
        
        # Track progress callbacks
        progress_messages = []
        def progress_callback(msg):
            progress_messages.append(msg)
        
        # Translate file
        result_path = translator.translate_vtt_file(
            self.vtt_file, 
            target_language="Vietnamese",
            progress_callback=progress_callback
        )
        
        # Verify success
        self.assertIsNotNone(result_path)
        self.assertTrue(result_path.exists())
        self.assertEqual(result_path.name, "test_video.vi.vtt")
        
        # Verify progress callbacks were called
        self.assertTrue(len(progress_messages) > 0)
        self.assertTrue(any("Parsing" in msg for msg in progress_messages))
        self.assertTrue(any("Translating" in msg for msg in progress_messages))
    
    def test_translate_vtt_file_no_client(self):
        """Test VTT file translation without API client"""
        translator = SubtitleTranslator()  # No API key
        
        result = translator.translate_vtt_file(self.vtt_file)
        self.assertIsNone(result)
    
    def test_translate_vtt_file_not_found(self):
        """Test VTT file translation with missing file"""
        translator = SubtitleTranslator(api_key="test-key")
        non_existent_file = self.temp_path / "missing.vtt"
        
        result = translator.translate_vtt_file(non_existent_file)
        self.assertIsNone(result)


class TestTranslateSubtitleFiles(unittest.TestCase):
    """Test cases for translate_subtitle_files function"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample video folder with VTT files
        self.video_folder = self.temp_path / "Test Video_abc123"
        self.video_folder.mkdir()
        
        # Create multiple VTT files
        vtt_files = [
            "Test Video.en.vtt",
            "Test Video.en-US.vtt", 
            "Test Video.vi.vtt"  # Already translated, should be skipped
        ]
        
        sample_content = """WEBVTT

00:00:01.000 --> 00:00:03.000
Test subtitle content.
"""
        
        for vtt_file in vtt_files:
            with open(self.video_folder / vtt_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_translate_subtitle_files_no_api_key(self):
        """Test translate_subtitle_files without API key"""
        result = translate_subtitle_files(self.video_folder)
        self.assertEqual(result, [])
    
    def test_translate_subtitle_files_no_vtt_files(self):
        """Test translate_subtitle_files with no VTT files"""
        empty_folder = self.temp_path / "empty"
        empty_folder.mkdir()
        
        result = translate_subtitle_files(empty_folder, api_key="test-key")
        self.assertEqual(result, [])
    
    @patch('core.translation.SubtitleTranslator')
    def test_translate_subtitle_files_success(self, mock_translator_class):
        """Test successful subtitle files translation"""
        # Setup mock translator
        mock_translator = MagicMock()
        mock_translator_class.return_value = mock_translator
        mock_translator.client = MagicMock()  # Simulate initialized client
        
        # Mock translation results
        translated_path1 = self.video_folder / "Test Video.vi.vtt"
        translated_path2 = self.video_folder / "Test Video2.vi.vtt"
        mock_translator.translate_vtt_file.side_effect = [translated_path1, translated_path2]
        
        result = translate_subtitle_files(
            self.video_folder,
            target_language="Vietnamese", 
            api_key="test-key"
        )
        
        # Should have translated 2 files (excluding the already translated .vi.vtt)
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_translator.translate_vtt_file.call_count, 2)
        
        # Verify translator was initialized correctly
        mock_translator_class.assert_called_once_with(api_key="test-key")


class TestTranslationIntegration(unittest.TestCase):
    """Integration tests for translation workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('core.translation.SubtitleTranslator')
    def test_full_workflow_with_progress(self, mock_translator_class):
        """Test complete translation workflow with progress tracking"""
        # Create video folder with VTT file
        video_folder = self.temp_path / "Video_123"
        video_folder.mkdir()
        
        vtt_file = video_folder / "video.en.vtt"
        with open(vtt_file, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello world\n")
        
        # Setup mock translator
        mock_translator = MagicMock()
        mock_translator_class.return_value = mock_translator
        mock_translator.client = MagicMock()
        
        translated_path = video_folder / "video.vi.vtt"
        mock_translator.translate_vtt_file.return_value = translated_path
        
        # Track progress
        progress_messages = []
        def progress_callback(msg):
            progress_messages.append(msg)
        
        # Run translation
        result = translate_subtitle_files(
            video_folder,
            target_language="Vietnamese",
            api_key="test-key", 
            progress_callback=progress_callback
        )
        
        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], translated_path)
        
        # Verify progress tracking
        mock_translator.translate_vtt_file.assert_called_once()
        call_args = mock_translator.translate_vtt_file.call_args
        self.assertEqual(call_args[0][0], vtt_file)  # VTT file path
        self.assertEqual(call_args[1]['target_language'], "Vietnamese")
        self.assertEqual(call_args[1]['progress_callback'], progress_callback)


if __name__ == '__main__':
    unittest.main(verbosity=2)