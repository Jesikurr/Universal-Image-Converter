"""Image conversion module for Universal Image Converter.

This module provides core functionality for converting images between
various formats using Pillow and pillow-heif libraries.
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from PIL import Image
import pillow_heif

import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

pillow_heif.register_heif_opener()


@dataclass(frozen=True)
class ConversionResult:
    """Structured result for image conversion operations."""

    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None


def _ensure_log_file() -> None:
    """Ensure the log file directory exists.

    Creates the parent directory for the log file if it doesn't exist.
    This prevents FileNotFoundError when writing to the log file.
    """
    try:
        log_dir = os.path.dirname(config.LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    except Exception as exc:
        logger.warning("Could not create log directory: %s", exc)


def _write_to_log(message: str) -> None:
    """Safely write a message to the log file.

    Args:
        message: Message to write to the log file

    This function handles errors gracefully if the log file cannot be written.
    """
    try:
        _ensure_log_file()
        with open(config.LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(message)
    except Exception as exc:
        logger.warning("Could not write to log file: %s", exc)


def get_supported_input_formats() -> List[str]:
    """Return a list of supported input image formats."""
    return list(config.SUPPORTED_INPUT_FORMATS)


def get_supported_output_formats() -> List[str]:
    """Return a list of supported output image formats."""
    return list(config.SUPPORTED_OUTPUT_FORMATS)


def _validate_conversion_inputs(in_path: str, out_dir: str, out_format: str) -> str:
    """Validate conversion inputs and return normalized output format."""
    if not os.path.isfile(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    normalized_format = out_format.lower().strip(".")
    if normalized_format not in get_supported_output_formats():
        raise ValueError(f"Unsupported output format: {out_format}")

    os.makedirs(out_dir, exist_ok=True)
    return normalized_format


def convert_image_detailed(in_path: str, out_dir: str, out_format: str) -> ConversionResult:
    """Convert a single image and return a structured result."""
    try:
        normalized_format = _validate_conversion_inputs(in_path, out_dir, out_format)
        pil_format = config.PILLOW_FORMAT_MAP.get(normalized_format, normalized_format.upper())

        base_name = os.path.splitext(os.path.basename(in_path))[0]
        ext = f".{normalized_format}"
        out_file = os.path.join(out_dir, base_name + ext)

        counter = 1
        while os.path.exists(out_file):
            out_file = os.path.join(out_dir, f"{base_name}_{counter}{ext}")
            counter += 1

        with Image.open(in_path) as image:
            if normalized_format == "ico":
                image = image.resize(config.ICO_DEFAULT_SIZE)
            image.save(out_file, format=pil_format)

        logger.info("Successfully converted: %s -> %s", in_path, out_file)
        _write_to_log(f"Converted: {in_path} -> {out_file}\n")
        return ConversionResult(success=True, output_path=out_file)
    except (FileNotFoundError, ValueError, OSError) as exc:
        error = str(exc)
        logger.error("Failed to convert %s: %s", in_path, error)
        _write_to_log(f"Failed: {in_path} -> {error}\n")
        return ConversionResult(success=False, error=error)
    except Exception as exc:
        error = f"Unexpected conversion error: {exc}"
        logger.exception("Unexpected error while converting %s", in_path)
        _write_to_log(f"Failed: {in_path} -> {error}\n")
        return ConversionResult(success=False, error=error)


def convert_image(in_path: str, out_dir: str, out_format: str) -> bool:
    """Backward-compatible conversion helper that returns only success/failure."""
    return convert_image_detailed(in_path, out_dir, out_format).success
