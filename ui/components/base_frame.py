"""Shared base frame with title header."""

import os

import customtkinter as ctk
from PIL import Image

from core.settings_manager import load_settings, resolve_path


class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, title, subtitle=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        if subtitle:
            ctk.CTkLabel(header, text=subtitle, font=ctk.CTkFont(size=13), text_color="gray").grid(
                row=1, column=0, sticky="w", pady=(4, 0)
            )

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)


def load_logo_image(size=(48, 48)):
    settings = load_settings()
    logo_path = resolve_path(settings.get("logo_path", "assets/logo.png"))
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    return None
