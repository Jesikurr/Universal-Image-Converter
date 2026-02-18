"""Graphical user interface for Universal Image Converter.

Provides a modern, themed GUI with drag-and-drop support, file browsing,
format selection, and theme switching capabilities.
"""

import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from PIL import Image, ImageTk
import ttkbootstrap as tb
import webbrowser
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES, TkinterDnD
from converter import convert_image, get_supported_output_formats

tkdnd_path = os.path.join(os.path.dirname(__file__), "tkdnd")
os.environ["TKDND_LIBRARY"] = os.path.join(tkdnd_path, "libtkdnd2.9.5.dll")

class ImageConverterApp:
    """Main GUI application class for Universal Image Converter.
    
    Manages the graphical interface including drag-and-drop functionality,
    file selection, format conversion, and theme switching.
    
    Attributes:
        app (TkinterDnD.Tk): Main application window
        style (tb.Style): ttkbootstrap style manager
        files (list): List of selected image file paths
        format_var (tk.StringVar): Selected output format
        theme_btn (tb.Button): Theme toggle button
    """
    
    def __init__(self):
        """Initialize the GUI application with all widgets and settings."""
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

        # Progress bar
        self.progress_frame = tb.Frame(main_frame)
        self.progress_frame.pack(fill=X, padx=10, pady=5)
        
        self.progress_bar = tb.Progressbar(
            self.progress_frame,
            mode='determinate',
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X, pady=5)
        
        self.progress_label = tb.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        # Hide progress initially
        self.progress_frame.pack_forget()

        self.convert_btn = tb.Button(main_frame, text="Convert Images", bootstyle="success", command=self.convert_all)
        self.convert_btn.pack(pady=(5, 15))

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
        """Start the image conversion process in a separate thread."""
        out_format = self.format_var.get()
        if not self.files or out_format == "Select output format":
            messagebox.showerror("Error", "Please select files and output format")
            return

        out_dir = filedialog.askdirectory(title="Choose Output Directory")
        if not out_dir:
            return

        # Disable UI during conversion
        self.convert_btn.config(state="disabled")
        self.format_combo.config(state="disabled")
        
        # Show progress bar
        self.progress_frame.pack(fill=X, padx=10, pady=5, before=self.convert_btn)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting conversion...")
        
        # Start conversion in separate thread
        thread = threading.Thread(
            target=self._convert_images_thread,
            args=(self.files.copy(), out_dir, out_format),
            daemon=True
        )
        thread.start()
    
    def _convert_images_thread(self, files, out_dir, out_format):
        """Perform image conversion in background thread.
        
        Args:
            files (list): List of file paths to convert
            out_dir (str): Output directory path
            out_format (str): Target output format
        """
        success = 0
        total = len(files)
        
        for idx, f in enumerate(files, 1):
            result = convert_image(f, out_dir, out_format)
            if result:
                success += 1
            
            # Update progress bar
            progress = (idx / total) * 100
            self.app.after(0, self._update_progress, progress, idx, total)
        
        # Conversion complete
        self.app.after(0, self._conversion_complete, success, total, out_format)
    
    def _update_progress(self, value, current, total):
        """Update progress bar and label (called from main thread).
        
        Args:
            value (float): Progress percentage (0-100)
            current (int): Current file number
            total (int): Total number of files
        """
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"Converting: {current}/{total} files")
        self.app.update_idletasks()
    
    def _conversion_complete(self, success, total, out_format):
        """Handle conversion completion (called from main thread).
        
        Args:
            success (int): Number of successfully converted files
            total (int): Total number of files processed
            out_format (str): Output format used
        """
        # Hide progress bar
        self.progress_frame.pack_forget()
        
        # Re-enable UI
        self.convert_btn.config(state="normal")
        self.format_combo.config(state="readonly")
        
        # Show result
        messagebox.showinfo(
            "Conversion Complete",
            f"Converted {success} of {total} files to {out_format.upper()}"
        )
        
        # Reset UI
        self.files = []
        self.drop_label.config(text="Drag and drop images here")

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = ImageConverterApp()
    app.run()
