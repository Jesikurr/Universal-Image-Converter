import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
import webbrowser
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from converter import convert_image, get_supported_output_formats

tkdnd_path = os.path.join(os.path.dirname(__file__), "tkdnd")
os.environ["TKDND_LIBRARY"] = os.path.join(tkdnd_path, "libtkdnd2.9.5.dll")

class ImageConverterApp:
    def __init__(self):
        self.app = TkinterDnD.Tk()
        self.style = tb.Style("darkly")

        self.app.title("Universal Image Converter")
        self.app.geometry("960x600")
        self.app.minsize(850, 500)
        self.files = []

        try:
            myappid = 'com.kurreations.imageconverter'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icon.ico")

        try:
            self.app.iconbitmap(default=icon_path)
        except tk.TclError:
            print("iconbitmap failed")

        self.init_theme_toggle()
        self.init_ui()

    def init_theme_toggle(self):
        def toggle():
            current = self.style.theme.name
            new_theme = "morph" if current == "darkly" else "darkly"
            self.style.theme_use(new_theme)
            self.theme_btn.config(text="Light Mode" if new_theme == "darkly" else "Dark Mode")

        self.theme_btn = tb.Button(self.app, text="Light Mode", command=toggle)
        self.theme_btn.pack(anchor="ne", padx=10, pady=10, ipadx=5, ipady=2)

    def init_ui(self):
        main_frame = tb.Frame(self.app)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.drop_frame = tb.LabelFrame(main_frame, text="Drop or Browse Images")
        self.drop_frame.pack(fill=BOTH, expand=True)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Drag and drop images here",
            anchor="center",
            bg="#2c2f33",
            fg="white",
            font=("Segoe UI", 11)
        )
        self.drop_label.pack(fill=BOTH, expand=True, pady=30, padx=10)

        try:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        except tk.TclError:
            self.drop_label.config(text="(Drag-and-drop unavailable. Use Browse.)")

        browse_btn = tb.Button(self.drop_frame, text="Browse Files", command=self.browse_files)
        browse_btn.pack(pady=10)

        self.format_var = tk.StringVar()
        self.format_combo = tb.Combobox(
            main_frame,
            textvariable=self.format_var,
            values=get_supported_output_formats(),
            state="readonly"
        )
        self.format_combo.pack(fill=X, padx=10, pady=(10, 5))
        self.format_combo.set("Select output format")

        convert_btn = tb.Button(main_frame, text="Convert Images", bootstyle="success", command=self.convert_all)
        convert_btn.pack(pady=(5, 15))

        donate_btn = tb.Button(self.app, text="💚 Support the Developer 💚", bootstyle="info", command=self.show_donation_info)
        donate_btn.pack(anchor="se", padx=10, pady=5, ipadx=5, ipady=2)

    def show_donation_info(self):
        url = "https://cash.app/$Jesikurr"
        webbrowser.open(url)

    def on_drop(self, event):
        raw = self.app.tk.splitlist(event.data)
        cleaned = [f.strip().strip('{}') for f in raw if os.path.isfile(f.strip().strip('{}'))]
        self.files = list(cleaned)
        self.drop_label.config(
            text=f"{len(self.files)} file(s) selected" if self.files else "Drag and drop images here"
        )

    def browse_files(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.heic *.tiff *.bmp *.webp *.ico")]
        self.files = filedialog.askopenfilenames(filetypes=filetypes)
        if self.files:
            self.drop_label.config(text=f"{len(self.files)} file(s) selected")

    def convert_all(self):
        out_format = self.format_var.get()
        if not self.files or out_format == "Select output format":
            messagebox.showerror("Error", "Please select files and output format")
            return

        out_dir = filedialog.askdirectory(title="Choose Output Directory")
        if not out_dir:
            return

        success = 0
        for f in self.files:
            result = convert_image(f, out_dir, out_format)
            if result:
                success += 1

        messagebox.showinfo("Conversion Complete", f"Converted {success} of {len(self.files)} files to {out_format.upper()}")
        self.files = []
        self.drop_label.config(text="Drag and drop images here")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = ImageConverterApp()
    app.run()
