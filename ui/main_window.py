"""Main application window with sidebar navigation."""

import os

import customtkinter as ctk

from core import database
from core.settings_manager import load_settings, resolve_path
from ui.components.base_frame import load_logo_image
from ui.templates.attendance_view import AttendanceView
from ui.templates.dashboard import DashboardView
from ui.templates.enroll_view import EnrollView
from ui.templates.reports_view import ReportsView
from ui.templates.settings_view import SettingsView


class MainWindow(ctk.CTk):
    NAV_ITEMS = [
        ("Dashboard", "dashboard"),
        ("Enroll", "enroll"),
        ("Mark Attendance", "attendance"),
        ("Reports", "reports"),
        ("Settings", "settings"),
    ]

    def __init__(self):
        super().__init__()

        settings = load_settings()
        self.title(settings.get("app_name", "Smart Student Attendance"))
        self.geometry("1100x700")
        self.minsize(900, 600)

        icon_path = resolve_path("assets/logo.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        self._build_sidebar_header(settings)
        self.nav_buttons = {}
        for i, (label, key) in enumerate(self.NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self.show_view(k),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=4)
            self.nav_buttons[key] = btn

        ctk.CTkLabel(
            self.sidebar,
            text="v1.0 | Windows",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).grid(row=8, column=0, sticky="sw", padx=15, pady=15)

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.views = {}
        self._current_view = None
        self.show_view("dashboard")

    def _build_sidebar_header(self, settings):
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(20, 15))

        logo = load_logo_image((48, 48))
        if logo:
            ctk.CTkLabel(header, image=logo, text="").pack(side="left", padx=(0, 10))

        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            text_frame,
            text=settings.get("app_name", "Smart Attendance"),
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=140,
            justify="left",
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_frame,
            text=settings.get("institution", ""),
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=140,
            justify="left",
        ).pack(anchor="w")

    def show_view(self, key):
        if self._current_view:
            self.views[self._current_view].grid_forget()

        for nav_key, btn in self.nav_buttons.items():
            btn.configure(fg_color=("gray75", "gray30") if nav_key == key else "transparent")

        if key not in self.views:
            self.views[key] = self._create_view(key)

        self.views[key].grid(row=0, column=0, sticky="nsew")
        self._current_view = key

        if key == "dashboard" and hasattr(self.views[key], "refresh"):
            self.views[key].refresh()

    def _create_view(self, key):
        if key == "dashboard":
            return DashboardView(self.content_area)
        if key == "enroll":
            return EnrollView(self.content_area)
        if key == "attendance":
            return AttendanceView(self.content_area, on_attendance_marked=self._on_attendance_marked)
        if key == "reports":
            return ReportsView(self.content_area)
        if key == "settings":
            return SettingsView(self.content_area, on_settings_saved=self._on_settings_saved)
        return DashboardView(self.content_area)

    def _on_attendance_marked(self):
        if "dashboard" in self.views:
            self.views["dashboard"].refresh()

    def _on_settings_saved(self):
        settings = load_settings()
        self.title(settings.get("app_name", "Smart Student Attendance"))


def run_app():
    database.create_tables()
    app = MainWindow()
    app.mainloop()
