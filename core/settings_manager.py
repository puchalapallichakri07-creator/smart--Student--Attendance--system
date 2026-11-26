"""Load, save, and reset application settings."""

import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")
DEFAULT_SETTINGS_PATH = os.path.join(BASE_DIR, "config", "default_settings.json")


def _ensure_settings_file():
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        shutil.copy(DEFAULT_SETTINGS_PATH, SETTINGS_PATH)


def load_settings():
    _ensure_settings_file()
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def reset_settings():
    shutil.copy(DEFAULT_SETTINGS_PATH, SETTINGS_PATH)
    return load_settings()


def resolve_path(relative_path):
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(BASE_DIR, relative_path)
