# Video File Organizer with AI Translation

A TUI video file organizer with Google Gemini AI-powered translation capabilities for SRT subtitle files. This tool helps you organize your video files and translate subtitle files to any supported language with AI translation.

## Features

### Core Features

- **File Organization**: Organize video files by language and format
- **VTT to SRT Conversion**: Convert WebVTT subtitle files to SRT format
- **Interactive TUI**: Beautiful terminal user interface with Rich library

### AI Translation Features ✨

- **SRT Translation**: Translate subtitle files using Google Gemini AI
- **Batch Translation**: Translate multiple SRT files simultaneously
- **Smart Language Detection**: Automatically detect source language from filenames
- **Concurrent Processing**: Fast translation with concurrent batch processing
- **Error Handling**: Robust retry logic with exponential backoff
- **Progress Tracking**: Real-time progress indication with detailed statistics
- **20+ Language Support**: Support for major world languages

## Project Structure

```
.
├── LICENSE
├── README.md
├── pyproject.toml
├── poetry.lock
└── src
    ├── __init__.py
    ├── main.py
    └── nichi
        ├── __init__.py
        ├── config/
        │   ├── __init__.py
        │   └── config_manager.py
        ├── core/
        │   ├── __init__.py
        │   ├── converter.py
        │   ├── organizer.py
        │   ├── operations.py
        │   ├── srt_parser.py
        │   ├── timing_adjuster.py
        │   └── translator.py
        ├── exceptions/
        │   └── __init__.py
        ├── models/
        │   └── __init__.py
        ├── services/
        │   ├── __init__.py
        │   ├── gemini_translator.py
        │   └── jellyfin_parser.py
        └── ui/
            ├── __init__.py
            ├── tui.py
            ├── ui_components.py
            └── user_input.py
```

## Installation

### Via PyPI (Recommended)

```bash
pip install nichi
```

### From Source

#### 1. Install Dependencies

This project now uses Poetry for dependency management. If you don't have Poetry installed, you can install it by following the [official instructions](https://python-poetry.org/docs/#installation).

```bash
# Install dependencies with Poetry
poetry install
```

#### 2. Set up Google AI API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Google Gemini
3. Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your configuration
GOOGLE_AI_API_KEY=your_actual_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
```

#### 3. Install the Package

```bash
# Activate the Poetry shell and run the application directly
poetry shell
python src/main.py

# Or run without activating the shell
poetry run python src/main.py

# To install in development mode
poetry install

# To build and install the package
poetry build
pip install dist/*.whl
```

## Usage

### Running the Application

```bash
# Run from current directory
python src/main.py

# Or if installed as package
nichi

# Show environment variables
python src/main.py --env
```

### Menu Options

1. **Convert VTT files to SRT format** - Convert WebVTT subtitle files to SRT format
2. **Organize MP4 and subtitle files into folders** - Group video files with their corresponding subtitle files
3. **Convert VTT files and then organize** - Perform both conversion and organization in sequence
4. **Show current directory contents** - Display the files in the current working directory
5. **Change working directory** - Navigate to a different directory
6. **Translate SRT file to another language** - Translate a single SRT file using Google Gemini AI
7. **Show available languages for translation** - Display all supported languages for translation
8. **Adjust subtitle timing** - Shift subtitle timing forward or backward
9. **Compare two Subtitle files** - Use git difftool to compare two SRT files
10. **Manage translation cache** - View and clear the translation cache
11. **Show environment variables** - Display relevant environment variables
12. **Exit** - Close the application

### Translation Features

The AI translation system offers:

- **Fast Processing**: Concurrent batch processing with configurable batch sizes (default: 200 entries)
- **Smart Retry**: Automatic retry with exponential backoff for failed requests
- **Progress Tracking**: Real-time progress bars with success/failure statistics
- **Language Auto-detection**: Automatically detects source language from filenames
- **Terminal User Interface**: Beautiful TUI with Rich library

## Supported Languages

| Code | Language | Code | Language   | Code | Language   |
| ---- | -------- | ---- | ---------- | ---- | ---------- |
| en   | English  | es   | Spanish    | fr   | French     |
| de   | German   | it   | Italian    | pt   | Portuguese |
| ru   | Russian  | ja   | Japanese   | ko   | Korean     |
| zh   | Chinese  | ar   | Arabic     | hi   | Hindi      |
| th   | Thai     | vi   | Vietnamese | nl   | Dutch      |
| sv   | Swedish  | da   | Danish     | no   | Norwegian  |
| fi   | Finnish  | pl   | Polish     | tr   | Turkish    |

## Configuration

### Environment Variables

Create a `.env` file with:

```bash

# Required Configuration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp

# Optional Configuration
# GOOGLE_AI_PROJECT_ID=your_project_id_here
# TRANSLATION_BATCH_SIZE=10
# DEFAULT_TARGET_LANGUAGE=id

# Optional Configuration (Gemini)
# GEMINI_MAX_RETRIES=3
# GEMINI_BASE_DELAY=1
# GEMINI_MAX_DELAY=60
```

## Performance

The translation system is optimized for speed:

- **Large Batches**: Processes 200 subtitle entries per batch by default
- **Concurrent Processing**: Handles up to 5 batches simultaneously
- **Smart Retry**: Exponential backoff prevents API rate limiting
- **Progress Tracking**: Real-time feedback on translation progress

## Troubleshooting

### Translation Not Available

If translation features are unavailable:

1. **Check API Key**: Ensure `.env` file exists with valid `GOOGLE_AI_API_KEY`
2. **Verify Installation**: Run `pip list | grep google-generativeai`
3. **Test Connection**: Check internet connectivity
4. **API Quota**: Verify your Google AI API has remaining quota

### Common Issues

**Encoding Errors**: The translator automatically handles UTF-8, Latin-1, and CP1252 encodings
**Rate Limiting**: The system includes automatic retry with exponential backoff
**Large Files**: For very large subtitle files, the system automatically splits them into manageable batches

## Security

- Keep your `.env` file secure and never commit it to version control
- Add `.env` to your `.gitignore` file
- API keys are only used for Google Gemini translation requests
- No subtitle content is stored or logged

## Development

### Code Structure

The project follows a clean architecture pattern:

- `config/` - Configuration management
- `core/` - Business logic and core functionality
- `exceptions/` - Custom exception classes
- `models/` - Data models and structures
- `services/` - External service integrations
- `ui/` - User interface components

### Code Quality

- Type hints for all functions and classes
- Comprehensive docstrings for all public interfaces
- Consistent naming conventions
- Modular design with clear separation of concerns

### Running Tests

```bash
# Run tests with Poetry
poetry run pytest
```

### Code Formatting

```bash
# Format code with black
poetry run black src/

# Sort imports with isort
poetry run isort src/
```

### Managing Dependencies

```bash
# Add a new dependency
poetry add package_name

# Add a new development dependency
poetry add --group dev package_name

# Update dependencies
poetry update

# Export dependencies to requirements.txt (if needed)
poetry export -o requirements.txt -f requirements.txt --without-hashes
```
