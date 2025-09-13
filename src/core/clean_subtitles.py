#!/usr/bin/env python3
"""
Clean subtitle files by removing translation artifacts.
Removes lines with "sau đây", "bản dịch", or "phụ đề" and their complete VTT entries.
"""

import re
from pathlib import Path

def clean_vietnamese_subtitle_file(file_path):
    """
    Clean a Vietnamese subtitle file by removing unwanted translation artifacts.
    Removes complete VTT entries containing "sau đây", "bản dịch", or "phụ đề".
    
    Args:
        file_path (str): Path to the .vi.vtt file to clean
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by double newlines to get individual VTT entries
        blocks = re.split(r'\n\n+', content.strip())
        
        cleaned_blocks = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            
            # Skip empty blocks
            if not lines or not any(line.strip() for line in lines):
                continue
            
            # Check if any line in this block contains unwanted Vietnamese phrases
            has_artifact = False
            for line in lines:
                if any(phrase in line.lower() for phrase in ['sau đây', 'bản dịch', 'phụ đề']):
                    has_artifact = True
                    print(f"Removing VTT entry with translation artifact: {line.strip()}")
                    break
            
            # Keep block only if it doesn't contain artifacts
            if not has_artifact:
                cleaned_blocks.append(block)
        
        # Reconstruct content
        cleaned_content = '\n\n'.join(cleaned_blocks)
        if cleaned_blocks:
            cleaned_content += '\n'
        
        # Write cleaned content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Cleaned: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return False

def find_and_clean_vietnamese_subtitles(base_dir="download-data"):
    """
    Find all Vietnamese subtitle files and clean them.
    
    Args:
        base_dir (str): Base directory to search for subtitle files
    """
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Directory {base_dir} does not exist.")
        return
    
    # Find all .vi.vtt files
    vietnamese_files = list(base_path.rglob("*.vi.vtt"))
    
    if not vietnamese_files:
        print("No Vietnamese subtitle files found.")
        return
    
    print(f"Found {len(vietnamese_files)} Vietnamese subtitle files:")
    
    cleaned_count = 0
    for file_path in vietnamese_files:
        print(f"Processing: {file_path}")
        if clean_vietnamese_subtitle_file(file_path):
            cleaned_count += 1
    
    print(f"\nCleaned {cleaned_count} files successfully.")

if __name__ == "__main__":
    find_and_clean_vietnamese_subtitles()