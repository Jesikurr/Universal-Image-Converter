"""Settings persistence for Universal Image Converter."""

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict

import config


@dataclass
class AppSettings:
    """Serializable UI settings."""

    theme: str = config.DEFAULT_THEME
    last_output_dir: str = ""
    last_output_format: str = ""


def _settings_file_path() -> str:
    """Return the settings file path in the user profile."""
    settings_dir = os.path.join(os.path.expanduser("~"), ".universal-image-converter")
    return os.path.join(settings_dir, "settings.json")


def _coerce_settings(data: Dict[str, Any]) -> AppSettings:
    """Coerce untrusted json data into AppSettings."""
    return AppSettings(
        theme=str(data.get("theme", config.DEFAULT_THEME)),
        last_output_dir=str(data.get("last_output_dir", "")),
        last_output_format=str(data.get("last_output_format", "")),
    )


def load_settings() -> AppSettings:
    """Load settings from disk with safe fallbacks."""
    path = _settings_file_path()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, dict):
            return _coerce_settings(raw)
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return AppSettings()


def save_settings(settings: AppSettings) -> None:
    """Persist settings to disk."""
    path = _settings_file_path()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(asdict(settings), handle, indent=2)
