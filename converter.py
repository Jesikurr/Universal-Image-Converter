"""Image conversion module for Universal Image Converter.

This module provides core functionality for converting images between
various formats using Pillow and pillow-heif libraries.
"""

import os
import logging
from PIL import Image
import pillow_heif

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

pillow_heif.register_heif_opener()

def get_supported_input_formats():
    """Return a list of supported input image formats.
    
    Returns:
        list: Lowercase file extensions without dots (e.g., ['jpg', 'png', 'heic'])
    """
    return ["jpg", "jpeg", "png", "heic", "webp", "tiff", "bmp", "ico"]

def get_supported_output_formats():
    """Return a list of supported output image formats.
    
    Returns:
        list: Lowercase file extensions without dots (e.g., ['jpg', 'png', 'heic'])
    """
    return ["jpg", "png", "webp", "tiff", "bmp", "ico", "heic"]

desktop_log_path = os.path.join(os.path.expanduser("~"), "Desktop", "conversion_log.txt")

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
        - Special handling for ICO format (resizes to 256x256)
        - Logs all conversions to Desktop/conversion_log.txt
        - Supports HEIC format through pillow-heif integration
    """
    try:
        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "webp": "WEBP",
            "tiff": "TIFF",
            "bmp": "BMP",
            "ico": "ICO",
            "heic": "HEIF"
        }
        pil_format = format_map.get(out_format.lower(), out_format.upper())

        base_name = os.path.splitext(os.path.basename(in_path))[0]
        ext = f".{out_format}"
        out_file = os.path.join(out_dir, base_name + ext)

        counter = 1
        while os.path.exists(out_file):
            out_file = os.path.join(out_dir, f"{base_name}_{counter}{ext}")
            counter += 1

        with Image.open(in_path) as im:
            if out_format.lower() == "ico":
                im = im.resize((256, 256))
            im.save(out_file, format=pil_format)

        logger.info(f"Successfully converted: {in_path} → {out_file}")
        with open(desktop_log_path, "a", encoding="utf-8") as log:
            log.write(f"✅ Converted: {in_path} → {out_file}\n")
        return True

    except Exception as e:
        logger.error(f"Failed to convert {in_path}: {e}")
        with open(desktop_log_path, "a", encoding="utf-8") as log:
            log.write(f"❌ Failed: {in_path} → {e}\n")
        return False
