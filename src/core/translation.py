#!/usr/bin/env python3
"""Translation module for YouTube Downloader using Claude API"""

import os
import re
import time
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import configuration settings
try:
    from config.settings import (
        TRANSLATION_BATCH_SIZE,
        TRANSLATION_RATE_LIMIT_DELAY,
        TRANSLATION_MAX_TOKENS,
        TRANSLATION_TIMEOUT
    )
except ImportError:
    # Fallback defaults if config not available
    TRANSLATION_BATCH_SIZE = 50
    TRANSLATION_RATE_LIMIT_DELAY = 0.5
    TRANSLATION_MAX_TOKENS = 8000
    TRANSLATION_TIMEOUT = 60


@dataclass
class VTTEntry:
    """Represents a single VTT subtitle entry"""
    index: int
    start_time: str
    end_time: str  
    text: str
    original_line: str  # Store original line for reconstruction


class SubtitleTranslator:
    """Handles VTT subtitle translation using Claude API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """Initialize translator with Claude API credentials"""
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if api_key and ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                logging.warning(f"Failed to initialize Anthropic client: {e}")
        elif not ANTHROPIC_AVAILABLE:
            logging.warning("Anthropic library not installed. Translation features disabled.")
    
    def translate_vtt_file(
        self, 
        vtt_path: Path, 
        target_language: str = "Vietnamese",
        progress_callback: Optional[Callable] = None
    ) -> Optional[Path]:
        """
        Translate a VTT file to target language preserving timing structure
        
        Args:
            vtt_path: Path to original VTT file
            target_language: Target language for translation
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to translated VTT file or None if translation failed
        """
        if not self.client:
            logging.error("Claude API client not initialized. Cannot translate subtitles.")
            return None
            
        if not vtt_path.exists():
            logging.error(f"VTT file not found: {vtt_path}")
            return None
        
        try:
            # Parse VTT content
            if progress_callback:
                progress_callback("🔍 Parsing subtitle structure...")
                
            vtt_entries = self._parse_vtt_file(vtt_path)
            if not vtt_entries:
                logging.warning(f"No subtitle entries found in {vtt_path}")
                return None
            
            logging.info(f"Found {len(vtt_entries)} subtitle entries to translate")
            
            # Extract text for translation
            texts_to_translate = [entry.text for entry in vtt_entries if entry.text.strip()]
            
            if not texts_to_translate:
                logging.warning("No text content found for translation")
                return None
            
            # Translate in batches
            if progress_callback:
                progress_callback(f"🌐 Translating {len(texts_to_translate)} subtitle entries...")
            
            translated_texts = self._translate_batch(texts_to_translate, target_language, progress_callback)
            
            if not translated_texts or len(translated_texts) != len(texts_to_translate):
                logging.error("Translation failed or incomplete")
                return None
            
            # Reconstruct VTT with translated text
            if progress_callback:
                progress_callback("📝 Rebuilding subtitle file...")
                
            translated_vtt_path = self._create_translated_vtt(
                vtt_path, vtt_entries, translated_texts, target_language
            )
            
            if progress_callback:
                progress_callback(f"✅ Translation completed: {translated_vtt_path.name}")
                
            logging.info(f"Successfully created translated VTT: {translated_vtt_path}")
            return translated_vtt_path
            
        except Exception as e:
            logging.error(f"Error translating VTT file: {e}")
            if progress_callback:
                progress_callback(f"❌ Translation failed: {str(e)}")
            return None
    
    def _parse_vtt_file(self, vtt_path: Path) -> List[VTTEntry]:
        """Parse VTT file and extract subtitle entries with timing"""
        entries = []
        
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by double newlines to get individual entries
        blocks = re.split(r'\n\n+', content.strip())
        
        for i, block in enumerate(blocks):
            lines = block.strip().split('\n')
            
            # Skip header and empty blocks
            if not lines or lines[0].startswith('WEBVTT') or not any(line.strip() for line in lines):
                continue
            
            # Find timing line (contains -->)
            timing_line = None
            text_lines = []
            
            for line in lines:
                if '-->' in line:
                    timing_line = line
                elif line.strip() and not line.isdigit():  # Skip index numbers
                    text_lines.append(line.strip())
            
            if timing_line and text_lines:
                # Parse timing
                timing_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})', timing_line)
                if timing_match:
                    start_time, end_time = timing_match.groups()
                    text = ' '.join(text_lines)
                    
                    entry = VTTEntry(
                        index=i,
                        start_time=start_time,
                        end_time=end_time,
                        text=text,
                        original_line=block
                    )
                    entries.append(entry)
        
        return entries
    
    def _translate_batch(
        self, 
        texts: List[str], 
        target_language: str,
        progress_callback: Optional[Callable] = None,
        batch_size: Optional[int] = None  # Use config default if not specified
    ) -> List[str]:
        """Translate text batch using Claude API with rate limiting"""
        # Use configuration defaults if not specified, adjust for model limitations
        if batch_size is None:
            if self.model == "claude-3-haiku-20240307":
                batch_size = min(TRANSLATION_BATCH_SIZE, 25)  # Smaller batch for Haiku model
            else:
                batch_size = TRANSLATION_BATCH_SIZE
            
        translated_texts = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(texts), batch_size):
            batch = texts[batch_idx:batch_idx + batch_size]
            current_batch_num = batch_idx // batch_size + 1
            
            if progress_callback:
                progress_callback(f"🌐 Translating batch {current_batch_num}/{total_batches}...")
            
            try:
                # Prepare batch for translation
                batch_text = '\n---SEPARATOR---\n'.join(batch)
                
                # Optimize API parameters for model limits - Claude Haiku has 4096 token limit
                if self.model == "claude-3-haiku-20240307":
                    max_tokens = min(4096, 2000 + len(batch) * 30)  # Conservative limit for Haiku
                else:
                    max_tokens = min(TRANSLATION_MAX_TOKENS, 4000 + len(batch) * 50)  # For other models
                
                # Call Claude API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.1,  # Low temperature for consistent translation
                    messages=[{
                        "role": "user",
                        "content": f"""Please translate the following subtitle text from English to {target_language}. 

IMPORTANT INSTRUCTIONS:
1. Translate each subtitle entry separately
2. Maintain the same number of entries as the input
3. Preserve the meaning and context
4. Keep translations natural and readable
5. Separate each translation with ---SEPARATOR---
6. Do not add explanations or extra text

Subtitle text to translate:
{batch_text}"""
                    }]
                )
                
                # Parse response
                translated_batch_text = response.content[0].text.strip()
                translated_batch = translated_batch_text.split('---SEPARATOR---')
                
                # Clean and validate translations
                translated_batch = [t.strip() for t in translated_batch]
                
                if len(translated_batch) != len(batch):
                    logging.warning(f"Batch translation count mismatch. Expected {len(batch)}, got {len(translated_batch)}")
                    # Pad or truncate to match
                    while len(translated_batch) < len(batch):
                        translated_batch.append(batch[len(translated_batch)])
                    translated_batch = translated_batch[:len(batch)]
                
                translated_texts.extend(translated_batch)
                
                # Dynamic rate limiting based on configuration and batch size
                if batch_idx + batch_size < len(texts):
                    # Use configured delay with dynamic adjustment for larger batches
                    delay = max(TRANSLATION_RATE_LIMIT_DELAY, TRANSLATION_RATE_LIMIT_DELAY * (1.0 - (batch_size / 200)))
                    time.sleep(delay)
                    
            except Exception as e:
                logging.error(f"Error translating batch {current_batch_num}: {e}")
                # Fallback: use original text for failed batch
                translated_texts.extend(batch)
        
        return translated_texts
    
    def _create_translated_vtt(
        self, 
        original_vtt_path: Path, 
        entries: List[VTTEntry], 
        translated_texts: List[str],
        target_language: str
    ) -> Path:
        """Create new VTT file with translated text preserving timing structure"""
        
        # Generate output filename
        base_name = original_vtt_path.stem
        if base_name.endswith('.en'):
            base_name = base_name[:-3]  # Remove .en suffix
        
        language_code = self._get_language_code(target_language)
        translated_path = original_vtt_path.parent / f"{base_name}.{language_code}.vtt"
        
        # Build VTT content
        vtt_content = ["WEBVTT", ""]
        
        text_index = 0
        for entry in entries:
            if entry.text.strip() and text_index < len(translated_texts):
                # Use translated text
                translated_text = translated_texts[text_index]
                text_index += 1
            else:
                # Fallback to original text
                translated_text = entry.text
            
            # Format VTT entry
            vtt_content.append(f"{entry.start_time} --> {entry.end_time}")
            vtt_content.append(translated_text)
            vtt_content.append("")  # Empty line between entries
        
        # Write translated VTT file
        with open(translated_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(vtt_content))
        
        return translated_path
    
    def _get_language_code(self, target_language: str) -> str:
        """Get language code for filename"""
        language_codes = {
            'vietnamese': 'vi',
            'spanish': 'es', 
            'french': 'fr',
            'german': 'de',
            'chinese': 'zh',
            'japanese': 'ja',
            'korean': 'ko'
        }
        return language_codes.get(target_language.lower(), 'trans')


def translate_subtitle_files(
    video_folder: Path,
    target_language: str = "Vietnamese", 
    api_key: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> List[Path]:
    """
    Translate all VTT files in a video folder
    
    Args:
        video_folder: Path to folder containing video and subtitles
        target_language: Target language for translation
        api_key: Claude API key
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of paths to created translated VTT files (includes existing ones)
    """
    # Find VTT files in folder
    vtt_files = list(video_folder.glob("*.vtt"))
    
    if not vtt_files:
        logging.info("No VTT subtitle files found for translation")
        return []
    
    translated_files = []
    language_code = SubtitleTranslator(api_key=api_key)._get_language_code(target_language)
    
    # First, check for native Vietnamese subtitles downloaded directly from YouTube
    native_vietnamese_files = [f for f in vtt_files if f.stem.endswith('.vi')]
    
    if native_vietnamese_files:
        if progress_callback:
            progress_callback(f"✅ Found native Vietnamese subtitles: {', '.join([f.name for f in native_vietnamese_files])}")
        logging.info(f"Using native Vietnamese subtitles from YouTube: {', '.join([f.name for f in native_vietnamese_files])}")
        return native_vietnamese_files
    
    # If no native Vietnamese subtitles, check for existing translated Vietnamese files
    for vtt_file in vtt_files:
        base_name = vtt_file.stem
        if base_name.endswith('.en'):
            base_name = base_name[:-3]  # Remove .en suffix
        
        expected_translated_path = video_folder / f"{base_name}.{language_code}.vtt"
        
        if expected_translated_path.exists():
            if progress_callback:
                progress_callback(f"✅ Using existing translated subtitles: {expected_translated_path.name}")
            logging.info(f"Using existing translated subtitles: {expected_translated_path.name}")
            translated_files.append(expected_translated_path)
    
    # If we found existing translations, return them
    if translated_files:
        return translated_files
    
    # No Vietnamese subtitles found - proceed with translation if API key is available
    if not api_key:
        if progress_callback:
            progress_callback("⚠️ No Vietnamese subtitles found and no API key for translation")
        logging.warning("No Vietnamese subtitles found and no Claude API key provided. Skipping subtitle translation.")
        return []
    
    translator = SubtitleTranslator(api_key=api_key)
    
    if not translator.client:
        logging.warning("Failed to initialize translator. Skipping subtitle translation.")
        return []
    
    # Translate English subtitles
    for vtt_file in vtt_files:
        # Skip already translated files
        if any(code in vtt_file.stem for code in ['.vi', '.es', '.fr', '.de', '.zh', '.ja', '.ko', '.trans']):
            continue
            
        logging.info(f"Translating subtitle file: {vtt_file.name}")
        
        translated_path = translator.translate_vtt_file(
            vtt_file, 
            target_language=target_language,
            progress_callback=progress_callback
        )
        
        if translated_path:
            translated_files.append(translated_path)
    
    return translated_files


if __name__ == "__main__":
    # Example usage
    import os
    
    # Test with a sample VTT file
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        test_folder = Path("download-data/test")
        translated_files = translate_subtitle_files(
            test_folder, 
            target_language="Vietnamese",
            api_key=api_key,
            progress_callback=lambda msg: print(f"[TRANSLATION] {msg}")
        )
        print(f"Translated {len(translated_files)} subtitle files")
    else:
        print("No ANTHROPIC_API_KEY environment variable found")