import os
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

def get_supported_input_formats():
    return ["jpg", "jpeg", "png", "heic", "webp", "tiff", "bmp", "ico"]

def get_supported_output_formats():
    return ["jpg", "png", "webp", "tiff", "bmp", "ico", "heic"]

desktop_log_path = os.path.join(os.path.expanduser("~"), "Desktop", "conversion_log.txt")

def convert_image(in_path, out_dir, out_format):
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

        with open(desktop_log_path, "a", encoding="utf-8") as log:
            log.write(f"✅ Converted: {in_path} → {out_file}\n")
        return True

    except Exception as e:
        with open(desktop_log_path, "a", encoding="utf-8") as log:
            log.write(f"❌ Failed: {in_path} → {e}\n")
        return False
