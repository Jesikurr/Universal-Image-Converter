"""Command-line interface for Universal Image Converter.

Provides a CLI for batch image conversion with support for individual
files or entire folders. Includes format validation and progress reporting.
"""

import argparse
import os
from converter import convert_image, get_supported_output_formats, get_supported_input_formats

def main():
    """Main entry point for the CLI application.
    
    Parses command-line arguments and executes image conversion based on
    user input. Supports single/multiple file conversion and batch folder
    processing.
    
    Command-line arguments:
        --input, -i: One or more input image file paths
        --input-folder: Directory containing images to convert
        --output-format, -f: Target output format (jpg, png, webp, etc.)
        --output-folder, -o: Directory for converted images
        --list-formats: Display all supported input/output formats
    
    Returns:
        None: Prints conversion results to stdout
    """
    parser = argparse.ArgumentParser(description="Universal Image Converter CLI")
    parser.add_argument("--input", "-i", nargs="+", help="Path(s) to image file(s)")
    parser.add_argument("--input-folder", help="Folder containing image files to convert")
    parser.add_argument("--output-format", "-f", choices=get_supported_output_formats(), help="Output format")
    parser.add_argument("--output-folder", "-o", help="Output directory")
    parser.add_argument("--list-formats", action="store_true", help="List all supported output formats")

    args = parser.parse_args()
    
    # Handle --list-formats flag
    if args.list_formats:
        print("Supported input formats:")
        print(", ".join(get_supported_input_formats()).upper())
        print("\nSupported output formats:")
        print(", ".join(get_supported_output_formats()).upper())
        return

    # Validate required arguments
    if not args.output_format:
        print("❌ Error: --output-format is required")
        parser.print_help()
        return
    
    if not args.output_folder:
        print("❌ Error: --output-folder is required")
        parser.print_help()
        return

    input_files = []

    if args.input_folder:
        for fname in os.listdir(args.input_folder):
            path = os.path.join(args.input_folder, fname)
            if os.path.isfile(path):
                ext = os.path.splitext(fname)[1].lower().strip(".")
                if ext in get_supported_input_formats():
                    input_files.append(path)

    if args.input:
        input_files.extend(args.input)

    if not input_files:
        print("❌ No input files found. Use --input or --input-folder with supported formats.")
        return

    total = len(input_files)
    success = 0

    for f in input_files:
        if os.path.isfile(f):
            result = convert_image(f, args.output_folder, args.output_format)
            if result:
                success += 1
        else:
            print(f"[SKIP] {f} is not a valid file.")

    print(f"Done. Converted {success} of {total} file(s) to {args.output_format.upper()}.")

if __name__ == "__main__":
    main()
