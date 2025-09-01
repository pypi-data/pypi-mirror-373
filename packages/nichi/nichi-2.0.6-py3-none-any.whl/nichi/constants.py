"""Constants used throughout the Video File Organizer application."""

# Environment variables
ENV_GOOGLE_AI_API_KEY = "GOOGLE_AI_API_KEY"
ENV_GEMINI_MODEL_NAME = "GEMINI_MODEL_NAME"
ENV_GOOGLE_AI_PROJECT_ID = "GOOGLE_AI_PROJECT_ID"
ENV_TRANSLATION_BATCH_SIZE = "TRANSLATION_BATCH_SIZE"
ENV_DEFAULT_TARGET_LANGUAGE = "DEFAULT_TARGET_LANGUAGE"
ENV_GEMINI_MAX_RETRIES = "GEMINI_MAX_RETRIES"
ENV_GEMINI_BASE_DELAY = "GEMINI_BASE_DELAY"
ENV_GEMINI_MAX_DELAY = "GEMINI_MAX_DELAY"

# Configuration paths
CONFIG_DIR = ".config/nichi"
CONFIG_FILE = ".env"
CONFIG_PATH_TEMPLATE = "~/%s/%s" % (CONFIG_DIR, CONFIG_FILE)
CACHE_DIR = "cache"

# Default values
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-exp"
DEFAULT_BATCH_SIZE = 200
DEFAULT_TARGET_LANGUAGE = "id"  # Indonesian
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1
DEFAULT_MAX_DELAY = 60

# File extensions
EXT_MP4 = ".mp4"
EXT_VTT = ".vtt"
EXT_SRT = ".srt"
EXT_EN_SRT = ".en.srt"

# File type extensions arrays
VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]
SUBTITLE_EXTENSIONS = [".srt", ".vtt", ".sub", ".idx", ".ssa", ".ass"]

# Menu choices
MENU_CHOICES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
