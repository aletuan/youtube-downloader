# YouTube Downloader

A professional Python-based YouTube video downloader with automatic subtitle translation, featuring a modern GUI built with Flet and powered by `yt-dlp`.

## Features

- High-Quality Video Downloads: Download YouTube videos in the best available quality
- Automatic Subtitle Translation: Translate English subtitles to Vietnamese (or other languages) using Claude API
- Video Preview: Preview video information before downloading
- Duplicate Detection: Smart detection of existing downloads with re-download options
- Progress Tracking: Real-time download progress with visual feedback
- Integrated Video Player: Built-in video player to watch downloaded content

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

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Usage

#### GUI Application (Recommended)

```bash
python src/gui/flet_app.py
```

#### Command Line

```bash
python youtube_downloader.py
```

#### Python Import

```python
from youtube_downloader import download_youtube_video
download_youtube_video("https://youtube.com/watch?v=...")
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Claude API Configuration (required for translation)
ANTHROPIC_API_KEY=your-api-key-here

# Translation Settings (optional)
TRANSLATION_ENABLED=true
TRANSLATION_TARGET_LANGUAGE=Vietnamese
TRANSLATION_MODEL=claude-3-haiku-20240307
```

### Getting a Claude API Key

1. Visit [Claude Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Add the key to your `.env` file

## Project Structure

```
├── src/                           # Modern modular implementation
│   ├── core/
│   │   ├── downloader.py         # Core download functionality
│   │   ├── translation.py        # Subtitle translation with Claude API
│   │   └── utils.py              # Utility functions
│   ├── config/
│   │   └── settings.py           # Configuration constants
│   └── gui/
│       ├── flet_app.py           # Main GUI application
│       ├── ui_factory.py         # UI component factory
│       ├── event_handlers.py     # GUI event handling
│       └── video_player.py       # Video player screen
├── tests/                         # Comprehensive test suite (89 tests)
├── youtube_downloader.py         # Backward compatibility wrapper
├── requirements.txt              # Python dependencies
├── .env                          # Environment configuration
└── download-data/                # Downloaded videos (auto-created)
```

## Features in Detail

### Video Download

- Downloads videos in the highest available quality
- Automatically downloads English subtitles (manual or auto-generated)
- Organizes each video in its own subfolder
- Smart filename sanitization for cross-platform compatibility

### Subtitle Translation

- Automatic translation of English subtitles to Vietnamese (configurable)
- Preserves exact VTT timing structure
- Non-destructive (keeps original English subtitles)
- Batch processing with rate limiting
- Progress tracking during translation

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
- Automatic subtitle display (both English and translated)
- Seamless navigation between main app and player

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_downloader.py -v
python -m pytest tests/test_translation.py -v

# Run with coverage
coverage run -m pytest tests/ -v
coverage report --show-missing
```

### Test Coverage

The project includes comprehensive test coverage with 89 tests:

- Core functionality: 15 tests
- Translation module: 16 tests  
- GUI framework: 11 tests
- Progress tracking: 11 tests
- UI factory: 10 tests
- Utility functions: 6 tests
- Validation: 20 tests

### Dependencies

- yt-dlp: Core video downloading (>= 2023.12.30)
- flet: Modern GUI framework (>= 0.21.0)
- anthropic: Claude API client for translation (>= 0.7.0)
- python-dotenv: Environment variable management (>= 1.0.0)

## File Organization

Downloaded videos are organized as follows:

```txt
download-data/
└── {VideoTitle}_{VideoID}/
    ├── {VideoTitle}.mp4        # Video file
    ├── {VideoTitle}.en.vtt     # Original English subtitles
    └── {VideoTitle}.vi.vtt     # Vietnamese translated subtitles
```

## Supported Languages

Translation supports multiple target languages:

- Vietnamese (vi) - Default
- TODO:
  - Spanish (es)
  - French (fr)
  - German (de)
  - Chinese (zh)
  - Japanese (ja)
  - Korean (ko)

## Troubleshooting

### Common Issues

1. Translation not working: Ensure `ANTHROPIC_API_KEY` is set in your `.env` file
2. Video download fails: Check your internet connection and YouTube URL validity
3. GUI not starting: Ensure Flet is properly installed: `pip install flet>=0.21.0`
4. Tests failing: Run `pip install -r requirements.txt` to ensure all dependencies are installed

### Error Handling

The application includes comprehensive error handling for:

- Network connectivity issues
- Invalid YouTube URLs
- Missing video files
- API rate limiting
- File system permissions

## License

This project is open source. Please ensure compliance with YouTube's Terms of Service when downloading content.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## Backward Compatibility

The project maintains backward compatibility with the original API through `youtube_downloader.py`, ensuring existing code continues to work while providing access to new modular features.
