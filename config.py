"""Configuration module for Universal Image Converter.

Centralizes application settings and constants to avoid hardcoded values
throughout the codebase.
"""

import os

# Application metadata
APP_NAME = "Universal Image Converter"
APP_ID = "com.kurreations.imageconverter"
APP_VERSION = "1.0.0"

# Window settings
DEFAULT_WINDOW_WIDTH = 960
DEFAULT_WINDOW_HEIGHT = 600
MIN_WINDOW_WIDTH = 850
MIN_WINDOW_HEIGHT = 500

# Theme settings
DEFAULT_THEME = "darkly"
LIGHT_THEME = "morph"
DARK_THEME = "darkly"

# Supported formats
SUPPORTED_INPUT_FORMATS = ["jpg", "jpeg", "png", "heic", "webp", "tiff", "bmp", "ico"]
SUPPORTED_OUTPUT_FORMATS = ["jpg", "png", "webp", "tiff", "bmp", "ico", "heic"]

# Format mapping for Pillow
PILLOW_FORMAT_MAP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "tiff": "TIFF",
    "bmp": "BMP",
    "ico": "ICO",
    "heic": "HEIF"
}

# Icon settings
ICO_DEFAULT_SIZE = (256, 256)

# Logging settings
LOG_FILE_NAME = "conversion_log.txt"
LOG_FILE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", LOG_FILE_NAME)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Developer support
DONATION_URL = "https://cash.app/$Jesikurr"
