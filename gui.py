"""Graphical user interface for Universal Image Converter.

Provides a modern, themed GUI with drag-and-drop support, file browsing,
format selection, and theme switching capabilities.
"""

import ctypes
import os
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
from typing import Any, List

import ttkbootstrap as tb
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkbootstrap.constants import BOTH, X

import config
from converter import convert_image, get_supported_output_formats


tkdnd_path = os.path.join(os.path.dirname(__file__), "tkdnd")
os.environ["TKDND_LIBRARY"] = os.path.join(tkdnd_path, "libtkdnd2.9.5.dll")


class ImageConverterApp:
    """Main GUI application class for Universal Image Converter."""

    def __init__(self) -> None:
        """Initialize the GUI application with all widgets and settings."""
        self.app = TkinterDnD.Tk()
        self.style = tb.Style(config.DEFAULT_THEME)

        self.app.title(config.APP_NAME)
        self.app.geometry(f"{config.DEFAULT_WINDOW_WIDTH}x{config.DEFAULT_WINDOW_HEIGHT}")
        self.app.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)

        self.files: List[str] = []
        self.format_var = tk.StringVar()

        self._set_windows_app_id()
        self._set_window_icon()

        self.init_theme_toggle()
        self.init_ui()

    def _set_windows_app_id(self) -> None:
        """Set custom Windows app id when available."""
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_ID)
        except Exception:
            pass

    def _resolve_base_path(self) -> str:
        """Resolve execution base path for frozen and source mode."""
        if getattr(sys, "frozen", False):
            return getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        return os.path.dirname(__file__)

    def _set_window_icon(self) -> None:
        """Load app icon from packaged and source-friendly paths."""
        base_path = self._resolve_base_path()
        icon_candidates = [
            os.path.join(base_path, "assets", "icon.ico"),
            os.path.join(base_path, "icon.ico"),
        ]

        for icon_path in icon_candidates:
            if not os.path.isfile(icon_path):
                continue
            try:
                self.app.iconbitmap(default=icon_path)
                return
            except tk.TclError:
                continue

    def init_theme_toggle(self) -> None:
        """Initialize the light/dark theme toggle button."""

        def toggle() -> None:
            current = self.style.theme.name
            new_theme = (
                config.LIGHT_THEME if current == config.DARK_THEME else config.DARK_THEME
            )
            self.style.theme_use(new_theme)
            self.theme_btn.config(
                text="Light Mode" if new_theme == config.DARK_THEME else "Dark Mode"
            )

        self.theme_btn = tb.Button(self.app, text="Light Mode", command=toggle)
        self.theme_btn.pack(anchor="ne", padx=10, pady=10, ipadx=5, ipady=2)

    def init_ui(self) -> None:
        """Build all UI widgets."""
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
            font=("Segoe UI", 11),
        )
        self.drop_label.pack(fill=BOTH, expand=True, pady=30, padx=10)

        try:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop)
        except tk.TclError:
            self.drop_label.config(text="(Drag-and-drop unavailable. Use Browse.)")

        browse_btn = tb.Button(self.drop_frame, text="Browse Files", command=self.browse_files)
        browse_btn.pack(pady=10)

        self.format_combo = tb.Combobox(
            main_frame,
            textvariable=self.format_var,
            values=get_supported_output_formats(),
            state="readonly",
        )
        self.format_combo.pack(fill=X, padx=10, pady=(10, 5))
        self.format_combo.set("Select output format")

        self.progress_frame = tb.Frame(main_frame)
        self.progress_frame.pack(fill=X, padx=10, pady=5)

        self.progress_bar = tb.Progressbar(
            self.progress_frame,
            mode="determinate",
            bootstyle="success-striped",
        )
        self.progress_bar.pack(fill=X, pady=5)

        self.progress_label = tb.Label(self.progress_frame, text="")
        self.progress_label.pack()

        self.progress_frame.pack_forget()

        self.convert_btn = tb.Button(
            main_frame,
            text="Convert Images",
            bootstyle="success",
            command=self.convert_all,
        )
        self.convert_btn.pack(pady=(5, 15))

        donate_btn = tb.Button(
            self.app,
            text="Support the Developer",
            bootstyle="info",
            command=self.show_donation_info,
        )
        donate_btn.pack(anchor="se", padx=10, pady=5, ipadx=5, ipady=2)

    def show_donation_info(self) -> None:
        """Open the developer donation page in default browser."""
        webbrowser.open(config.DONATION_URL)

    def on_drop(self, event: Any) -> None:
        """Handle drag-and-drop files from OS."""
        raw = self.app.tk.splitlist(event.data)
        cleaned = [
            file_path.strip().strip("{}")
            for file_path in raw
            if os.path.isfile(file_path.strip().strip("{}"))
        ]
        self.files = list(cleaned)
        self.drop_label.config(
            text=f"{len(self.files)} file(s) selected"
            if self.files
            else "Drag and drop images here"
        )

    def browse_files(self) -> None:
        """Open file picker and update selected files."""
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.heic *.tiff *.bmp *.webp *.ico")]
        selected_files = filedialog.askopenfilenames(filetypes=filetypes)
        self.files = list(selected_files)
        if self.files:
            self.drop_label.config(text=f"{len(self.files)} file(s) selected")

    def convert_all(self) -> None:
        """Start the image conversion process in a separate thread."""
        out_format = self.format_var.get()
        if not self.files or out_format == "Select output format":
            messagebox.showerror("Error", "Please select files and output format")
            return

        out_dir = filedialog.askdirectory(title="Choose Output Directory")
        if not out_dir:
            return

        self.convert_btn.config(state="disabled")
        self.format_combo.config(state="disabled")

        self.progress_frame.pack(fill=X, padx=10, pady=5, before=self.convert_btn)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Starting conversion...")

        thread = threading.Thread(
            target=self._convert_images_thread,
            args=(list(self.files), out_dir, out_format),
            daemon=True,
        )
        thread.start()

    def _convert_images_thread(self, files: List[str], out_dir: str, out_format: str) -> None:
        """Perform image conversion in background thread."""
        success = 0
        total = len(files)

        for idx, file_path in enumerate(files, 1):
            result = convert_image(file_path, out_dir, out_format)
            if result:
                success += 1

            progress = (idx / total) * 100
            self.app.after(0, self._update_progress, progress, idx, total)

        self.app.after(0, self._conversion_complete, success, total, out_format)

    def _update_progress(self, value: float, current: int, total: int) -> None:
        """Update progress bar and label (called from main thread)."""
        self.progress_bar["value"] = value
        self.progress_label.config(text=f"Converting: {current}/{total} files")
        self.app.update_idletasks()

    def _conversion_complete(self, success: int, total: int, out_format: str) -> None:
        """Handle conversion completion (called from main thread)."""
        self.progress_frame.pack_forget()

        self.convert_btn.config(state="normal")
        self.format_combo.config(state="readonly")

        messagebox.showinfo(
            "Conversion Complete",
            f"Converted {success} of {total} files to {out_format.upper()}",
        )

        self.files = []
        self.drop_label.config(text="Drag and drop images here")

    def run(self) -> None:
        """Run the Tk main loop."""
        self.app.mainloop()


if __name__ == "__main__":
    app = ImageConverterApp()
    app.run()
