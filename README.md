# YouTube Downloader

A professional Python-based YouTube video downloader featuring a modern GUI built with Flet and powered by `yt-dlp`.

## Features

- **High-Quality Video Downloads**: Download YouTube videos in the best available quality
- **Default Subtitle Support**: Downloads available subtitles as provided by YouTube
- **Video Preview**: Preview video information before downloading
- **Duplicate Detection**: Smart detection of existing downloads with re-download options
- **Progress Tracking**: Real-time download progress with visual feedback
- **Integrated Video Player**: Built-in video player to watch downloaded content

## Quick Start

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd youtube-downloader
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```


### Usage

#### GUI Application (Recommended)

```bash
python src/gui/download_screen.py
```

#### Python Import

```python
from src.core.downloader import download_youtube_video
download_youtube_video("https://youtube.com/watch?v=...")
```

## Configuration

No additional configuration required. The application works out of the box with default settings:

- Downloads videos in best available quality
- Downloads subtitles when available from YouTube
- Saves files to your system's Downloads folder in a `youtube-downloader` subdirectory

## Project Structure

```
├── src/                           # Modern modular implementation
│   ├── core/
│   │   ├── downloader.py         # Core download functionality
│   │   └── utils.py              # Utility functions
│   ├── config/
│   │   └── settings.py           # Configuration constants
│   └── gui/
│       ├── download_screen.py     # Main GUI application
│       ├── ui_factory.py         # UI component factory
│       ├── event_handlers.py     # GUI event handling
│       └── video_player_screen.py # Video player screen
├── tests/                         # Comprehensive test suite (85 tests)
├── requirements.txt              # Python dependencies
└── download-data/                # Downloaded videos (auto-created)
```

## Features in Detail

### Video Download

- Downloads videos in the highest available quality
- Automatically downloads subtitles when available (manual or auto-generated)
- Organizes each video in its own subfolder
- Smart filename sanitization for cross-platform compatibility

### GUI Interface

- Modern Material Design interface
- Video preview with metadata display
- Download progress tracking with visual feedback
- Duplicate detection with user choice options
- Integrated video player for downloaded content
- Responsive design with proper error handling

### Video Player

- Built-in video player with standard controls
- Support for multiple video formats (.mp4, .mkv, .webm, .avi, .mov, .m4v, .flv)
- Automatic subtitle display when available
- Seamless navigation between main app and player

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_downloader.py -v
python -m pytest tests/test_utils.py -v

# Run with coverage
coverage run -m pytest tests/ -v
coverage report --show-missing
```

### Test Coverage

The project includes comprehensive test coverage with 85 tests:

- Core functionality: 15 tests
- GUI framework: 11 tests
- Progress tracking: 11 tests
- UI factory: 10 tests
- Utility functions: 6 tests
- Validation: 20 tests
- Downloads folder: 12 tests

### Dependencies

- yt-dlp: Core video downloading (>= 2023.12.30)
- flet: Modern GUI framework (>= 0.21.0)

## File Organization

Downloaded videos are organized as follows:

```txt
download-data/
└── {VideoTitle}_{VideoID}/
    ├── {VideoTitle}.mp4        # Video file
    └── {VideoTitle}.en.vtt     # Subtitles (if available)
```

## Supported Subtitle Languages

The application downloads subtitles in whatever languages are available from YouTube, commonly including:

- English (en, en-US)
- And any other languages provided by the video uploader

## Troubleshooting

### Common Issues

1. **Video download fails**: Check your internet connection and YouTube URL validity
2. **GUI not starting**: Ensure Flet is properly installed: `pip install flet>=0.21.0`
3. **Tests failing**: Run `pip install -r requirements.txt` to ensure all dependencies are installed
4. **No subtitles downloaded**: Not all videos have subtitles available - this is normal

### Error Handling

The application includes comprehensive error handling for:

- Network connectivity issues
- Invalid YouTube URLs
- Missing video files
- File system permissions
- Video availability and restrictions

## License

This project is open source. Please ensure compliance with YouTube's Terms of Service when downloading content.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## Modern Architecture

The project uses a clean modular architecture with separation of concerns between core functionality, configuration, and GUI components, making it easy to maintain and extend.
