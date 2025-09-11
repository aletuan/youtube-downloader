# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based YouTube video downloader that uses yt-dlp to download videos with subtitles. Each video is organized into its own subfolder within a `download-data/` directory structure. The project follows a modular architecture with professional Python project structure.

## Core Architecture

### Modular Structure (src/ directory)

- **`src/core/downloader.py`**: Core YouTube download functionality
  - **`download_youtube_video(url, output_dir)`**: Main download function
  - **`_get_video_info(url)`**: Extract video metadata without downloading
  - **`_check_video_exists(output_dir, video_title, video_id)`**: Check for existing downloads with duplicate detection
  - **`_create_video_folder(output_dir, video_title, video_id)`**: Create video-specific folders
  - **`_get_yt_dlp_options(video_folder)`**: Configure yt-dlp download options

- **`src/core/utils.py`**: Utility functions
  - **`sanitize_filename(filename)`**: Remove invalid filesystem characters

- **`src/config/settings.py`**: Configuration constants
  - Default output directory, subtitle languages, video format settings

- **`src/gui/flet_app.py`**: GUI application using Flet framework
  - Modern Material Design interface with preview and duplicate detection
  - Threading support for non-blocking downloads and video info fetching
  - Dynamic UI states for existing video handling (re-download workflow)

### Backward Compatibility

- **`youtube_downloader.py`**: Compatibility wrapper maintaining original API
  - Imports from new modular structure
  - Preserves all original function signatures
  - Maintains backward compatibility for existing users

### Key Dependencies

- **yt-dlp**: Core video downloading functionality (version >= 2023.12.30)
- **flet**: Modern Python GUI framework (version >= 0.21.0)
- **pathlib**: Modern path handling
- **re**: Filename sanitization

## Development Commands

### Testing

```bash
# Run all tests with pytest (preferred - new modular structure)
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_downloader.py -v
python -m pytest tests/test_utils.py -v
python -m pytest tests/test_flet_setup.py -v

# Run single test class
python -m pytest tests/test_downloader.py::TestGetVideoInfo -v

# Run single test method
python -m pytest tests/test_downloader.py::TestDownloadYoutubeVideo::test_download_video_success -v

# Legacy compatibility wrapper testing
python -c "from youtube_downloader import download_youtube_video; print('Import test passed')"
```

### Coverage Analysis

```bash
# Run tests with coverage (new structure)
coverage run -m pytest tests/ -v

# Generate coverage report
coverage report --show-missing

# Generate HTML coverage report
coverage html
```

### Running Applications

```bash
# Run YouTube downloader (interactive mode)
python youtube_downloader.py

# Run Flet GUI application
python src/gui/flet_app.py

# Direct usage (import in Python)
from youtube_downloader import download_youtube_video
download_youtube_video("https://youtube.com/watch?v=...")
```

## Testing Architecture

The modular test suite in `tests/` directory uses unittest with mocking to avoid network calls:

### Test Structure

- **`tests/test_downloader.py`**: 15 tests covering core download functionality
  - TestGetVideoInfo: Video metadata extraction (3 tests)
  - TestCreateVideoFolder: Folder creation logic (3 tests)
  - TestGetYtDlpOptions: Configuration testing (2 tests)
  - TestCheckVideoExists: Duplicate detection functionality (5 tests)
  - TestDownloadYoutubeVideo: End-to-end download testing (2 tests)
  
- **`tests/test_utils.py`**: 6 tests covering utility functions
  - TestSanitizeFilename: Filename sanitization edge cases
  
- **`tests/test_flet_setup.py`**: 11 tests covering GUI framework
  - TestFletFramework: Flet import and component creation (4 tests)
  - TestGUIIntegration: GUI integration with core functionality (4 tests)
  - TestGUIErrorHandling: Error handling scenarios (3 tests)

### Testing Strategy

- **Mocking Strategy**: Uses `MagicMock` to simulate yt-dlp's `YoutubeDL` context manager
- **Temp Directories**: All file system tests use temporary directories for isolation
- **Network Isolation**: No actual network calls during testing
- **Total Coverage**: 32 tests across all modules with comprehensive coverage

## File Organization

```text
├── src/                           # Modern modular implementation
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py         # Core download functionality
│   │   └── utils.py              # Utility functions
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py           # Configuration constants
│   └── gui/
│       ├── __init__.py
│       └── flet_app.py           # GUI application (Flet framework)
├── tests/                         # Modern test suite
│   ├── __init__.py
│   ├── test_downloader.py        # Core functionality tests (15 tests)
│   ├── test_utils.py             # Utility tests (6 tests)
│   └── test_flet_setup.py        # GUI framework tests (11 tests)
├── youtube_downloader.py         # Backward compatibility wrapper
├── requirements.txt              # Python dependencies (yt-dlp, flet)
├── CLAUDE.md                     # This documentation file
├── download-data/                # Created automatically, contains downloaded videos
│   └── {VideoTitle}_{VideoID}/
│       ├── {VideoTitle}.mp4
│       └── {VideoTitle}.en.vtt
└── cookies/                      # Optional cookies for authentication
```

## yt-dlp Configuration

The downloader is configured with these key options:

- `format: 'best'` - Downloads highest quality available
- `writesubtitles: True` - Downloads manual subtitles if available
- `writeautomaticsub: True` - Falls back to auto-generated subtitles
- `subtitleslangs: ['en', 'en-US']` - English subtitle preference
- `subtitlesformat: 'vtt'` - WebVTT subtitle format

## Testing Guidelines

When modifying the download function:

1. Mock yt-dlp interactions to avoid network calls
2. Use temporary directories for file system tests
3. Test both success and error scenarios
4. Verify folder structure and file naming
5. Check yt-dlp configuration options are passed correctly

### Mocking Pattern

The mocking pattern for the new modular structure:

```python
# For core functionality testing
@patch('core.downloader.yt_dlp.YoutubeDL')
def test_function(self, mock_yt_dlp):
    mock_ydl_instance = MagicMock()
    mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
    # Configure mock behavior...

# For backward compatibility testing  
@patch('youtube_downloader.yt_dlp.YoutubeDL')  # Still works via import chain
def test_legacy_function(self, mock_yt_dlp):
    # Test compatibility wrapper behavior...
```

### Development Phases

The project supports multiple development phases:

1. **✅ Phase 1 Complete**: Professional project structure reorganization
2. **✅ Phase 2 Complete**: YouTube Downloader GUI implementation using Flet
   - Modern Material Design interface with Flet framework
   - Video preview with metadata extraction
   - Duplicate detection and re-download workflow
   - Threading support for non-blocking operations
   - Enhanced error handling and user feedback
3. **Phase 3 (Future)**: Advanced features and optimizations
   - Batch download support
   - Quality/format selection options
   - Download progress tracking
   - Playlist support
   - Advanced subtitle options

Current status: Full-featured YouTube downloader with modern GUI and comprehensive duplicate detection.
