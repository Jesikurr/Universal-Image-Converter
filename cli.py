"""Command-line interface for Universal Image Converter.

Provides a CLI for batch image conversion with support for individual
files or entire folders. Includes format validation and progress reporting.
"""

import argparse
import logging
import os
from typing import List, Optional, Sequence

from converter import (
    convert_image_detailed,
    get_supported_input_formats,
    get_supported_output_formats,
)

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI parser."""
    parser = argparse.ArgumentParser(description="Universal Image Converter CLI")
    parser.add_argument("--input", "-i", nargs="+", help="Path(s) to image file(s)")
    parser.add_argument("--input-folder", help="Folder containing image files to convert")
    parser.add_argument(
        "--output-format",
        "-f",
        choices=get_supported_output_formats(),
        help="Output format",
    )
    parser.add_argument("--output-folder", "-o", help="Output directory")
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List all supported output formats",
    )
    return parser


def collect_input_files(
    input_paths: Optional[Sequence[str]], input_folder: Optional[str]
) -> List[str]:
    """Collect valid input files from explicit paths and optional folder."""
    input_files: List[str] = []
    supported_input_formats = set(get_supported_input_formats())

    if input_folder:
        if not os.path.isdir(input_folder):
            raise NotADirectoryError(f"Input folder does not exist: {input_folder}")

        for filename in os.listdir(input_folder):
            path = os.path.join(input_folder, filename)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(filename)[1].lower().strip(".")
            if ext in supported_input_formats:
                input_files.append(path)

    if input_paths:
        input_files.extend(input_paths)

    # Preserve order while deduplicating.
    return list(dict.fromkeys(input_files))


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse arguments and execute image conversion.

    Returns:
        Exit code where 0 means success and non-zero indicates an error.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_formats:
        print("Supported input formats:")
        print(", ".join(get_supported_input_formats()).upper())
        print("\nSupported output formats:")
        print(", ".join(get_supported_output_formats()).upper())
        return 0

    if not args.output_format:
        logger.error("Missing required argument: --output-format")
        print("Error: --output-format is required")
        parser.print_help()
        return 2

    if not args.output_folder:
        logger.error("Missing required argument: --output-folder")
        print("Error: --output-folder is required")
        parser.print_help()
        return 2

    try:
        os.makedirs(args.output_folder, exist_ok=True)
        input_files = collect_input_files(args.input, args.input_folder)
    except (NotADirectoryError, OSError) as exc:
        logger.error("Invalid input/output path: %s", exc)
        print(f"Error: {exc}")
        return 2

    if not input_files:
        logger.warning("No valid input files found")
        print("No input files found. Use --input or --input-folder with supported formats.")
        return 2

    logger.info(
        "Starting batch conversion of %s file(s) to %s",
        len(input_files),
        args.output_format.upper(),
    )

    total = len(input_files)
    success = 0

    for file_path in input_files:
        if not os.path.isfile(file_path):
            logger.warning("Skipping invalid file: %s", file_path)
            print(f"[SKIP] {file_path} is not a valid file.")
            continue

        result = convert_image_detailed(file_path, args.output_folder, args.output_format)
        if result.success:
            success += 1
        else:
            print(f"[FAIL] {file_path}: {result.error}")

    logger.info(
        "Batch conversion complete: %s/%s files converted successfully",
        success,
        total,
    )
    print(f"Done. Converted {success} of {total} file(s) to {args.output_format.upper()}.")

    return 0 if success == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
