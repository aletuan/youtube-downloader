# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based YouTube video downloader that uses yt-dlp to download videos with subtitles. Each video is organized into its own subfolder within a `download-data/` directory structure.

## Core Architecture

### Main Module: `youtube_downloader.py`

- **`sanitize_filename(filename)`**: Utility function that removes invalid filesystem characters (`<>:"/\|?*`) and replaces them with underscores
- **`download_youtube_video(url, output_dir="download-data")`**: Main download function that:
  1. Extracts video metadata (title, ID) without downloading
  2. Creates sanitized folder: `{video_title}_{video_id}/`
  3. Downloads video and subtitles to that folder
  4. Configures yt-dlp for subtitle download (English VTT format)

### Key Dependencies

- **yt-dlp**: Core video downloading functionality (version >= 2023.12.30)
- **pathlib**: Modern path handling
- **re**: Filename sanitization

## Development Commands

### Testing

```bash
# Run all tests with pytest (preferred)
python -m pytest test_youtube_downloader.py -v

# Run tests with standard unittest
python test_youtube_downloader.py

# Run single test class
python -m pytest test_youtube_downloader.py::TestSanitizeFilename -v

# Run single test method
python -m pytest test_youtube_downloader.py::TestDownloadYoutubeVideo::test_download_video_success -v
```

### Coverage Analysis

```bash
# Run tests with coverage
coverage run -m pytest test_youtube_downloader.py -v

# Generate coverage report
coverage report --show-missing

# Generate HTML coverage report
coverage html
```

### Running the Script

```bash
# Interactive mode
python youtube_downloader.py

# Direct usage (import in Python)
from youtube_downloader import download_youtube_video
download_youtube_video("https://youtube.com/watch?v=...")
```

## Testing Architecture

The test suite (`test_youtube_downloader.py`) uses unittest with mocking to avoid network calls:

- **TestSanitizeFilename**: 6 tests covering filename sanitization edge cases
- **TestDownloadYoutubeVideo**: 7 tests using `unittest.mock` to mock yt-dlp interactions
- **Mocking Strategy**: Uses `MagicMock` to simulate yt-dlp's `YoutubeDL` context manager
- **Temp Directories**: All file system tests use temporary directories for isolation
- **Coverage**: Achieves 93% coverage (missing only interactive input lines)

## File Organization

```
├── youtube_downloader.py      # Main module with download logic
├── test_youtube_downloader.py # Comprehensive test suite
├── requirements.txt           # Python dependencies
├── download-data/             # Created automatically, contains downloaded videos
│   └── {VideoTitle}_{VideoID}/
│       ├── {VideoTitle}.mp4
│       └── {VideoTitle}.en.vtt
└── cookies/                   # Optional cookies for authentication
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

The mocking pattern follows:

```python
@patch('youtube_downloader.yt_dlp.YoutubeDL')
def test_function(self, mock_yt_dlp):
    mock_ydl_instance = MagicMock()
    mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
    # Configure mock behavior...
```
