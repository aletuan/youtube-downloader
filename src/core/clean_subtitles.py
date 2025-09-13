#!/usr/bin/env python3
"""
Clean subtitle files by removing translation artifacts and HTML-like tags.
Removes lines with "sau đây", "bản dịch", or "phụ đề" and their complete VTT entries.
Also removes HTML-like tags such as <c>, </c>, <00:03:09.360>, etc.
"""

import re
from pathlib import Path

def clean_html_tags(text):
    """
    Remove HTML-like tags from subtitle text.
    
    Args:
        text (str): Text containing HTML-like tags
        
    Returns:
        str: Text with HTML-like tags removed
    """
    # Remove timestamp tags like <00:03:09.360>
    text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
    
    # Remove other HTML-like tags like <c>, </c>, <i>, </i>, etc.
    text = re.sub(r'<[^>]*>', '', text)
    
    # Clean up extra spaces that may result from tag removal
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

# Note: _has_translation_artifacts function removed - now doing line-by-line detection in _clean_vtt_block

def _clean_vtt_block(lines, remove_artifacts=True, remove_html_tags=True):
    """
    Clean a single VTT block (subtitle entry).

    Args:
        lines (list): Lines of the VTT block
        remove_artifacts (bool): Whether to check for translation artifacts
        remove_html_tags (bool): Whether to remove HTML tags

    Returns:
        tuple: (should_keep: bool, cleaned_lines: list)
    """
    # Skip empty blocks
    if not lines or not any(line.strip() for line in lines):
        return False, []

    cleaned_lines = []

    for line in lines:
        # Keep timing lines as-is (contain -->)
        if '-->' in line:
            cleaned_lines.append(line)
        elif line.strip() and not line.isdigit():
            # Check for translation artifacts in individual lines
            if remove_artifacts:
                if any(phrase in line.lower() for phrase in ['sau đây', 'bản dịch', 'phụ đề', 'vietnamese translation', 'here\'s the vietnamese', 'here are the vietnamese']):
                    # Skip this line as it contains artifacts
                    continue

            # Process text content lines
            if remove_html_tags:
                original_line = line
                cleaned_line = clean_html_tags(line)

                # Only report if tags were actually removed (debug logging disabled)
                # if original_line != cleaned_line:
                #     print(f"Cleaned HTML tags from: {original_line.strip()}")
                #     print(f"Result: {cleaned_line}")

                # Only add non-empty lines
                if cleaned_line.strip():
                    cleaned_lines.append(cleaned_line)
            else:
                # Keep line as-is if not cleaning HTML tags
                cleaned_lines.append(line)
        else:
            # Keep other lines (like index numbers)
            cleaned_lines.append(line)

    # Remove empty lines and ensure proper spacing
    final_lines = []
    for line in cleaned_lines:
        if line.strip():  # Only keep non-empty lines
            final_lines.append(line)

    # Only keep block if it has content after cleaning
    return bool(final_lines and any(line.strip() for line in final_lines)), final_lines

def _process_vtt_file(file_path, remove_artifacts=True, remove_html_tags=True):
    """
    Core VTT file processing function.
    
    Args:
        file_path (str): Path to VTT file
        remove_artifacts (bool): Whether to remove translation artifacts
        remove_html_tags (bool): Whether to remove HTML tags
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by double newlines to get individual VTT entries
        blocks = re.split(r'\n\n+', content.strip())
        
        cleaned_blocks = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            should_keep, cleaned_lines = _clean_vtt_block(lines, remove_artifacts, remove_html_tags)
            
            if should_keep:
                cleaned_blocks.append('\n'.join(cleaned_lines))
        
        # Reconstruct content with compact VTT spacing
        # No empty lines between timing lines and content
        cleaned_content = '\n\n'.join(cleaned_blocks)
        if cleaned_blocks:
            cleaned_content += '\n'
        
        # Final pass: remove empty lines after timing lines
        lines = cleaned_content.split('\n')
        final_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            final_lines.append(line)

            # If this is a timing line, skip any empty lines that follow
            if '-->' in line:
                i += 1
                # Skip empty lines after timing line
                while i < len(lines) and not lines[i].strip():
                    i += 1
                # Don't increment i here, let the main loop handle the next line
                continue
            else:
                i += 1

        final_content = '\n'.join(final_lines)

        # Write cleaned content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Public API functions with clear purposes

def clean_vietnamese_subtitle_file(file_path):
    """
    Clean Vietnamese subtitle file by removing both translation artifacts and HTML tags.
    
    Args:
        file_path (str): Path to the .vi.vtt file to clean
        
    Returns:
        bool: True if successful, False otherwise
    """
    result = _process_vtt_file(file_path, remove_artifacts=True, remove_html_tags=True)
    # if result:
    #     print(f"Cleaned artifacts and HTML tags from: {file_path}")
    return result

def clean_html_tags_only(file_path):
    """
    Clean only HTML tags from subtitle file, keeping translation artifacts.
    
    Args:
        file_path (str): Path to the .vi.vtt file to clean
        
    Returns:
        bool: True if successful, False otherwise
    """
    result = _process_vtt_file(file_path, remove_artifacts=False, remove_html_tags=True)
    # if result:
    #     print(f"Cleaned HTML tags from: {file_path}")
    return result

def clean_vietnamese_translation_artifacts(vtt_path):
    """
    Main cleaning function used by translation module.
    Removes both Vietnamese translation artifacts and HTML tags.
    
    Args:
        vtt_path (str or Path): Path to Vietnamese VTT file to clean
        
    Returns:
        bool: True if successful, False otherwise
    """
    return clean_vietnamese_subtitle_file(str(vtt_path))

def find_and_clean_vietnamese_subtitles(base_dir="download-data", clean_tags_only=False):
    """
    Find all Vietnamese subtitle files and clean them.
    
    Args:
        base_dir (str): Base directory to search for subtitle files
        clean_tags_only (bool): If True, only clean HTML tags without removing artifacts
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
    
    action = "Cleaning HTML tags only from" if clean_tags_only else "Processing"
    print(f"Found {len(vietnamese_files)} Vietnamese subtitle files:")
    
    cleaned_count = 0
    for file_path in vietnamese_files:
        print(f"{action}: {file_path}")
        
        if clean_tags_only:
            success = clean_html_tags_only(file_path)
        else:
            success = clean_vietnamese_subtitle_file(file_path)
        
        if success:
            cleaned_count += 1
    
    action_past = "HTML tags cleaned from" if clean_tags_only else "Cleaned"
    print(f"\n{action_past} {cleaned_count} files successfully.")

if __name__ == "__main__":
    find_and_clean_vietnamese_subtitles()