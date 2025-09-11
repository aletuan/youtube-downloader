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
  - Real-time download progress tracking with visual feedback
  - Integrated video player with screen navigation after successful downloads

### Backward Compatibility

- **`youtube_downloader.py`**: Compatibility wrapper maintaining original API
  - Imports from new modular structure
  - Preserves all original function signatures
  - Maintains backward compatibility for existing users

### Key Dependencies

- **yt-dlp**: Core video downloading functionality (version >= 2023.12.30)
- **flet**: Modern Python GUI framework (version >= 0.21.0)
- **anthropic**: Claude API client for subtitle translation (version >= 0.7.0)
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
│       ├── flet_app.py           # Main GUI application (Flet framework)
│       ├── ui_factory.py         # UI component factory functions
│       ├── event_handlers.py     # GUI event handling logic
│       └── video_player.py       # Video player screen with navigation
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

## Subtitle Translation Feature

### Overview

The YouTube Downloader now includes automatic subtitle translation using the Claude API. After downloading English subtitles, the system automatically translates them to Vietnamese (or other configurable languages) while preserving the exact timing structure of the original VTT files.

### Key Features

- **Automatic Translation**: Subtitles are translated immediately after video download completes
- **Timing Preservation**: Original VTT timing structure is maintained perfectly
- **Non-Destructive**: Original English subtitles are kept alongside translated versions
- **Smart File Naming**: Translated files use language codes (e.g., `video.vi.vtt` for Vietnamese)
- **Progress Tracking**: Real-time progress updates in the GUI during translation
- **Error Handling**: Robust error handling with fallback to original subtitles on failure
- **Rate Limiting**: Built-in API rate limiting to respect Claude API limits

### Setup Instructions

1. **Install Dependencies**:

   ```bash
   pip install anthropic>=0.7.0
   ```

2. **Get Claude API Key**:
   - Visit <https://console.anthropic.com/>
   - Create an account and generate an API key
   - Store the key securely

3. **Configure API Key**:
   Set the `ANTHROPIC_API_KEY` environment variable:

   ```bash
   # On macOS/Linux
   export ANTHROPIC_API_KEY="your-api-key-here"
   
   # On Windows
   set ANTHROPIC_API_KEY=your-api-key-here
   ```

4. **Configuration Options** (in `src/config/settings.py`):

   ```python
   TRANSLATION_ENABLED = True  # Enable/disable translation
   TRANSLATION_TARGET_LANGUAGE = 'Vietnamese'  # Target language
   TRANSLATION_MODEL = 'claude-3-haiku-20240307'  # Claude model to use
   TRANSLATION_BATCH_SIZE = 10  # Subtitles per API call
   TRANSLATION_RATE_LIMIT_DELAY = 1.0  # Seconds between API calls
   ```

### File Structure After Translation

```text
download-data/
└── {VideoTitle}_{VideoID}/
    ├── {VideoTitle}.mp4        # Video file
    ├── {VideoTitle}.en.vtt     # Original English subtitles
    └── {VideoTitle}.vi.vtt     # Vietnamese translated subtitles
```

### Translation Workflow

1. **Video Download**: yt-dlp downloads video + English subtitles
2. **VTT Parsing**: System parses VTT structure, extracting timing and text
3. **Batch Translation**: Text content is sent to Claude API in batches
4. **VTT Reconstruction**: Translated text is combined with original timing
5. **File Creation**: New `.vi.vtt` file is created alongside original
6. **GUI Update**: User sees "Translation completed" status

### Supported Languages

The translation system supports multiple target languages:

- Vietnamese (vi)
- Spanish (es)  
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

### Usage in Video Player

The video player automatically detects both original and translated subtitle files, allowing users to choose between English and Vietnamese subtitles during playback.

### API Usage and Costs

- Uses Claude 3 Haiku model for cost-effective translation
- Typical cost: ~$0.01-0.05 per video subtitle file
- Rate limited to respect API quotas
- Automatic retry logic for temporary failures

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

1. **[x] Phase 1 Complete**: Professional project structure reorganization
2. **[x] Phase 2 Complete**: YouTube Downloader GUI implementation using Flet
   - Modern Material Design interface with Flet framework
   - Video preview with metadata extraction
   - Duplicate detection and re-download workflow
   - Threading support for non-blocking operations
   - Enhanced error handling and user feedback
3. **Phase 3**: Advanced features and optimizations
   - [x] Download progress tracking with real-time updates
   - **Video Player Feature** (Mostly Complete):
     - [x] Basic video player screen layout and navigation
     - [x] Play button integration that appears after successful downloads
     - [x] Video file path detection and tracking from local downloads
     - [x] Screen routing system for navigation between main app and player
     - [x] Back navigation from player to main screen (fixed view stack management)
     - [x] Video player component with Flet Video widget loading local files
     - [x] Local video file playback with absolute path support
     - [x] Auto-play functionality when video screen loads
     - [x] Built-in video controls (native play/pause/stop/seek)
     - [x] Error handling for missing video files and unsupported formats
     - [x] Simplified UI design (removed redundant controls and info sections)
     - [x] Multiple video format support (.mp4, .mkv, .webm, .avi, .mov, .m4v, .flv)videos
     - [x] Subtitle display integration in video player
   - [ ] Quality/format selection options
   - [ ] Playlist support
   - [x] **Advanced Subtitle Translation** (Complete):
     - [x] Claude API integration for subtitle translation
     - [x] Vietnamese translation support with configurable target language
     - [x] VTT format parsing and reconstruction preserving timing structure
     - [x] Batch translation with rate limiting and error handling
     - [x] GUI progress tracking for translation phase
     - [x] Automatic translation after successful video download
     - [x] Non-destructive translation (keeps original English subtitles)
     - [x] Comprehensive test coverage (16 tests)
   - [ ] Quality/format selection options
   - [ ] Playlist support

Current status: Full-featured YouTube downloader with modern GUI, comprehensive duplicate detection, download progress tracking, integrated video player functionality, automatic subtitle translation using Claude API, and environment variable configuration with .env file support. The project includes 89 comprehensive tests and is ready for production use.

## Environment Configuration

### .env File Support

The project now includes comprehensive environment variable support through python-dotenv:

1. **Automatic .env Loading**: Both `src/config/settings.py` and `src/core/translation.py` automatically load environment variables from a `.env` file in the project root.

2. **Configuration Variables**:
   - `ANTHROPIC_API_KEY`: Claude API key for subtitle translation
   - `TRANSLATION_ENABLED`: Enable/disable translation feature (true/false)
   - `TRANSLATION_TARGET_LANGUAGE`: Target language for translation (default: Vietnamese)
   - `TRANSLATION_MODEL`: Claude model to use (default: claude-3-haiku-20240307)

3. **Auth Conflict Resolution**: Using .env files resolves authentication conflicts between Claude Code OAuth tokens and the ANTHROPIC_API_KEY environment variable.

4. **Fallback Defaults**: All environment variables have sensible defaults, so the application works even without a .env file.

### Example .env File

```env
# YouTube Downloader Environment Variables
# Claude API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key-here

# Translation Settings (optional overrides)
TRANSLATION_ENABLED=true
TRANSLATION_TARGET_LANGUAGE=Vietnamese
TRANSLATION_MODEL=claude-3-haiku-20240307
```
