import argparse
import os
from converter import convert_image, get_supported_output_formats

def main():
    parser = argparse.ArgumentParser(description="Universal Image Converter CLI")
    parser.add_argument("--input", "-i", nargs="+", help="Path(s) to image file(s)")
    parser.add_argument("--input-dir", help="Folder containing image files to convert")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--format", "-f", required=True, choices=get_supported_output_formats(), help="Output format")

    args = parser.parse_args()

    input_files = []

    if args.input_dir:
        for fname in os.listdir(args.input_dir):
            path = os.path.join(args.input_dir, fname)
            if os.path.isfile(path):
                ext = os.path.splitext(fname)[1].lower().strip(".")
                if ext in get_supported_output_formats():
                    input_files.append(path)

    if args.input:
        input_files.extend(args.input)

    if not input_files:
        print("❌ No input files found. Use --input or --input-dir with supported formats.")
        return

    total = len(input_files)
    success = 0

    for f in input_files:
        if os.path.isfile(f):
            result = convert_image(f, args.output, args.format)
            if result:
                success += 1
        else:
            print(f"[SKIP] {f} is not a valid file.")

    print(f"Done. Converted {success} of {total} file(s) to {args.format.upper()}.")

if __name__ == "__main__":
    main()
