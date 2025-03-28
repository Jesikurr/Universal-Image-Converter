import os
import sys
import platform
import tkinter as tk
from tkinter import filedialog, ttk
import tkinterdnd2
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import pillow_heif
import webbrowser

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

if platform.system() == "Windows":
    tkinterdnd2.TkinterDnD.TKDND_LIBRARY = os.path.join(base_path, "tkdnd")

icon_path = os.path.join(base_path, "Universal_Converter_icon.ico")
icon_image_path = os.path.join(base_path, "Universal_Converter_icon.ico")

pillow_heif.register_heif_opener()

KOFI_URL = "https://ko-fi.com/jesikurr"
SUPPORTED_INPUTS = tuple(Image.registered_extensions().keys())

DARK_BG = "#2b1b35"
LIGHT_BG = "#f0f0f0"
LIGHT_FG = "#000000"
DARK_FG = "#ffffff"
ACCENT = "#b799e4"
ACCENT_HOVER = "#d3bdf0"
FOOTER_LIGHT = "#666666"
FOOTER_DARK = "#dddddd"
BUTTON_FONT = ("Segoe UI", 11, "bold")
LABEL_FONT = ("Segoe UI", 14, "bold")

format_map = {
    "JPG": "JPEG",
    "PNG": "PNG",
    "WEBP": "WEBP",
    "TIFF": "TIFF",
    "BMP": "BMP"
}

def get_unique_filename(base_path):
    if not os.path.exists(base_path):
        return base_path
    base, ext = os.path.splitext(base_path)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def open_image(file_path):
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":
            os.system(f"open \"{file_path}\"")
        else:
            os.system(f"xdg-open \"{file_path}\"")
    except Exception as e:
        status_label.config(text=f"⚠️ Couldn't open image: {e}")

def convert_image(file_path, open_after=True, save_to=None):
    try:
        image = Image.open(file_path)
        output_key = format_dropdown.get()
        output_format = format_map.get(output_key, output_key)
        output_ext = f".{output_key.lower()}"
        filename = os.path.basename(file_path)
        new_name = os.path.splitext(filename)[0] + output_ext
        if save_to:
            output_path = os.path.join(save_to, new_name)
        else:
            output_path = os.path.splitext(file_path)[0] + output_ext
        output_path = get_unique_filename(output_path)
        image.save(output_path, output_format.upper())
        status_label.config(text=f"✅ Saved: {output_path}")
        if open_after:
            open_image(output_path)
    except Exception as e:
        status_label.config(text=f"❌ Conversion failed: {e}")

def on_drop(event):
    file_path = event.data.strip("{}")
    status_label.config(text="⏳ Converting...")
    root.update()
    convert_image(file_path)

def on_browse():
    file_path = filedialog.askopenfilename(filetypes=[("All images", "*.*")])
    if file_path:
        status_label.config(text="⏳ Converting...")
        root.update()
        convert_image(file_path)

def on_batch():
    folder_path = filedialog.askdirectory(title="Select Folder with Images")
    if not folder_path:
        return
    save_path = filedialog.askdirectory(title="Select Destination Folder")
    if not save_path:
        return
    converted = 0
    for file in os.listdir(folder_path):
        if file.lower().endswith(SUPPORTED_INPUTS):
            full_path = os.path.join(folder_path, file)
            convert_image(full_path, open_after=False, save_to=save_path)
            converted += 1
    status_label.config(text=f"✅ Converted {converted} file(s) to: {save_path}")

def toggle_dark_mode():
    dark = root.cget("bg") == DARK_BG
    bg = LIGHT_BG if dark else DARK_BG
    fg = LIGHT_FG if dark else DARK_FG
    footer_fg = FOOTER_LIGHT if dark else FOOTER_DARK
    label.config(bg=bg, fg=fg, font=LABEL_FONT, highlightbackground=ACCENT, highlightthickness=3)
    format_label.config(bg=bg, fg=fg)
    browse_button.config(bg=ACCENT, fg="black")
    batch_button.config(bg=ACCENT, fg="black")
    darkmode_button.config(bg=ACCENT, fg="black")
    format_dropdown.config(background=ACCENT, foreground="black")
    status_label.config(bg=bg, fg=fg)
    footer.config(bg=bg, fg=footer_fg)
    header_frame.config(bg=bg)
    app_name.config(bg=bg, fg=fg)
    root.config(bg=bg)

def open_kofi():
    webbrowser.open(KOFI_URL)

root = TkinterDnD.Tk()
root.title("Universal Image Converter")
root.geometry("500x500")
root.configure(bg=DARK_BG)
root.resizable(False, False)

if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

header_frame = tk.Frame(root, bg=DARK_BG)
header_frame.pack(pady=(10, 5))

if os.path.exists(icon_image_path):
    try:
        icon_img = Image.open(icon_image_path).resize((24, 24))
        icon_tk = ImageTk.PhotoImage(icon_img)
        icon_label = tk.Label(header_frame, image=icon_tk, bg=DARK_BG)
        icon_label.image = icon_tk
        icon_label.pack(side="left", padx=(0, 5))
    except Exception as e:
        pass

app_name = tk.Label(header_frame, text="Universal Image Converter", font=("Segoe UI", 14, "bold"), bg=DARK_BG, fg=DARK_FG)
app_name.pack(side="left")

label = tk.Label(root, text="Drop your image file here", font=LABEL_FONT, relief="ridge", width=40, height=4,
                 bg=DARK_BG, fg=DARK_FG, highlightbackground=ACCENT, highlightthickness=3)
label.pack(pady=10)

format_label = tk.Label(root, text="Select output format:", font=("Segoe UI", 11), bg=DARK_BG, fg=DARK_FG)
format_label.pack(pady=(10, 0))

format_dropdown = ttk.Combobox(root, values=list(format_map.keys()), state="readonly")
format_dropdown.set("JPG")
format_dropdown.pack(pady=5)

browse_button = tk.Button(root, text="Browse and Upload", command=on_browse, font=BUTTON_FONT, bg=ACCENT,
                          activebackground=ACCENT_HOVER, relief="groove", fg="black")
browse_button.pack(pady=3)

batch_button = tk.Button(root, text="Batch Convert Folder", command=on_batch, font=BUTTON_FONT, bg=ACCENT,
                         activebackground=ACCENT_HOVER, relief="groove", fg="black")
batch_button.pack(pady=3)

darkmode_button = tk.Button(root, text="Disable Dark Mode", command=toggle_dark_mode, font=BUTTON_FONT, bg=ACCENT,
                             activebackground=ACCENT_HOVER, relief="groove", fg="black")
darkmode_button.pack(pady=3)

status_label = tk.Label(root, text="", font=("Segoe UI", 10), bg=DARK_BG, fg=DARK_FG)
status_label.pack(pady=5)

footer = tk.Label(root, text="Made with 💜 by Jesikurr · Support on Ko-fi", font=("Segoe UI", 10, "italic"),
                  bg=DARK_BG, fg=FOOTER_DARK, cursor="hand2")
footer.pack(side="bottom", pady=5)
footer.bind("<Button-1>", lambda e: open_kofi())

label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", on_drop)

root.mainloop()
