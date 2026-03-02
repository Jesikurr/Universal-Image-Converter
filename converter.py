"""Image conversion module for Universal Image Converter.

This module provides core functionality for converting images between
various formats using Pillow and pillow-heif libraries.
"""

import os
import logging
from PIL import Image
import pillow_heif
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

pillow_heif.register_heif_opener()

def _ensure_log_file():
    """Ensure the log file directory exists.
    
    Creates the parent directory for the log file if it doesn't exist.
    This prevents FileNotFoundError when writing to the log file.
    """
    try:
        log_dir = os.path.dirname(config.LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create log directory: {e}")

def _write_to_log(message):
    """Safely write a message to the log file.
    
    Args:
        message (str): Message to write to the log file
    
    This function handles errors gracefully if the log file cannot be written.
    """
    try:
        _ensure_log_file()
        with open(config.LOG_FILE_PATH, "a", encoding="utf-8") as log:
            log.write(message)
    except Exception as e:
        logger.warning(f"Could not write to log file: {e}")

def get_supported_input_formats():
    """Return a list of supported input image formats.
    
    Returns:
        list: Lowercase file extensions without dots (e.g., ['jpg', 'png', 'heic'])
    """
    return config.SUPPORTED_INPUT_FORMATS

def get_supported_output_formats():
    """Return a list of supported output image formats.
    
    Returns:
        list: Lowercase file extensions without dots (e.g., ['jpg', 'png', 'heic'])
    """
    return config.SUPPORTED_OUTPUT_FORMATS

def convert_image(in_path, out_dir, out_format):
    """Convert a single image file to the specified format.
    
    Args:
        in_path (str): Full path to the input image file
        out_dir (str): Directory where the converted image will be saved
        out_format (str): Target output format (e.g., 'jpg', 'png', 'webp')
    
    Returns:
        bool: True if conversion succeeded, False if it failed
    
    Notes:
        - Automatically handles filename collisions by appending _1, _2, etc.
        - Special handling for ICO format (resizes to configured size)
        - Logs all conversions to desktop log file
        - Supports HEIC format through pillow-heif integration
    """
    try:
        pil_format = config.PILLOW_FORMAT_MAP.get(out_format.lower(), out_format.upper())

        base_name = os.path.splitext(os.path.basename(in_path))[0]
        ext = f".{out_format}"
        out_file = os.path.join(out_dir, base_name + ext)

        counter = 1
        while os.path.exists(out_file):
            out_file = os.path.join(out_dir, f"{base_name}_{counter}{ext}")
            counter += 1

        with Image.open(in_path) as im:
            if out_format.lower() == "ico":
                im = im.resize(config.ICO_DEFAULT_SIZE)
            im.save(out_file, format=pil_format)

        logger.info(f"Successfully converted: {in_path} → {out_file}")
        _write_to_log(f"✅ Converted: {in_path} → {out_file}\n")
        return True

    except Exception as e:
        logger.error(f"Failed to convert {in_path}: {e}")
        _write_to_log(f"❌ Failed: {in_path} → {e}\n")
        return False
