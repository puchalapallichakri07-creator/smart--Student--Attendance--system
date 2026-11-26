"""Application settings screen."""

import os
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from core.settings_manager import load_settings, reset_settings, resolve_path, save_settings
from modules.fingerprint_module import fingerprint_module
from ui.components.base_frame import BaseFrame, load_logo_image


class SettingsView(BaseFrame):
    def __init__(self, master, on_settings_saved=None, **kwargs):
        super().__init__(master, title="Settings", subtitle="Configure attendance methods and devices", **kwargs)
        self.on_settings_saved = on_settings_saved
        self.settings = load_settings()
        self._entries = {}

        scroll = ctk.CTkScrollableFrame(self.content)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(1, weight=1)

        row = 0
        row = self._section(scroll, row, "General")
        row = self._entry_row(scroll, row, "App Name", "app_name")
        row = self._entry_row(scroll, row, "Institution", "institution")
        row = self._logo_row(scroll, row)

        row = self._section(scroll, row, "Attendance Methods")
        self.method_vars = {}
        for key, label in [
            ("qr_code", "QR Code"),
            ("face_recognition", "Face Recognition"),
            ("fingerprint", "Fingerprint (R307)"),
            ("scanner", "Scanner"),
        ]:
            var = ctk.BooleanVar(value=self.settings["methods"].get(key, True))
            self.method_vars[key] = var
            ctk.CTkCheckBox(scroll, text=label, variable=var).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)
            row += 1

        row = self._section(scroll, row, "Face Recognition")
        row = self._slider_row(scroll, row, "Match Threshold", "face", "match_threshold", 0.4, 0.8)
        row = self._spin_row(scroll, row, "Camera Index", "face", "camera_index", 0, 4)

        row = self._section(scroll, row, "QR / Scanner")
        row = self._spin_row(scroll, row, "Scanner Camera", "scanner", "camera_index", 0, 4)
        self.scanner_beep = ctk.BooleanVar(value=self.settings.get("scanner", {}).get("beep_on_success", True))
        ctk.CTkCheckBox(scroll, text="Beep on successful scan", variable=self.scanner_beep).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4
        )
        row += 1

        row = self._section(scroll, row, "Fingerprint (R307 — COM3)")
        self.fp_enabled = ctk.BooleanVar(value=self.settings.get("fingerprint", {}).get("enabled", True))
        ctk.CTkCheckBox(scroll, text="Enable fingerprint module", variable=self.fp_enabled).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4
        )
        row += 1

        ctk.CTkLabel(scroll, text="COM Port").grid(row=row, column=0, sticky="w", padx=10, pady=4)
        self.fp_port = ctk.CTkComboBox(scroll, values=[f"COM{i}" for i in range(1, 9)])
        self.fp_port.set(self.settings.get("fingerprint", {}).get("port", "COM3"))
        self.fp_port.grid(row=row, column=1, sticky="ew", padx=10, pady=4)
        row += 1

        row = self._spin_row(scroll, row, "Scan Timeout (sec)", "fingerprint", "scan_timeout_sec", 5, 30)

        fp_btns = ctk.CTkFrame(scroll, fg_color="transparent")
        fp_btns.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        ctk.CTkButton(fp_btns, text="Test Connection", command=self.test_fingerprint).pack(side="left", padx=5)
        ctk.CTkButton(fp_btns, text="Test Scan", command=self.test_scan).pack(side="left", padx=5)
        row += 1

        self.fp_status = ctk.CTkLabel(scroll, text="", wraplength=500, justify="left", text_color="gray")
        self.fp_status.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)
        row += 1

        row = self._section(scroll, row, "Reports")
        ctk.CTkLabel(scroll, text="Export Folder").grid(row=row, column=0, sticky="w", padx=10, pady=4)
        export_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        export_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=4)
        export_frame.grid_columnconfigure(0, weight=1)
        self.export_path = ctk.CTkEntry(export_frame)
        self.export_path.insert(0, self.settings.get("reports", {}).get("export_path", "reports"))
        self.export_path.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(export_frame, text="Browse", width=80, command=self.browse_export).grid(row=0, column=1)
        row += 1

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=20, padx=10)
        ctk.CTkButton(btn_row, text="Save Settings", command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Reset Defaults", fg_color="gray", command=self.reset).pack(side="left", padx=5)

    def _section(self, parent, row, title):
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5)
        )
        return row + 1

    def _entry_row(self, parent, row, label, key):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=4)
        entry = ctk.CTkEntry(parent)
        entry.insert(0, self.settings.get(key, ""))
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=4)
        self._entries[key] = entry
        return row + 1

    def _slider_row(self, parent, row, label, section, key, from_, to):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=4)
        val = self.settings.get(section, {}).get(key, (from_ + to) / 2)
        var = ctk.DoubleVar(value=val)
        slider = ctk.CTkSlider(parent, from_=from_, to=to, variable=var)
        slider.grid(row=row, column=1, sticky="ew", padx=10, pady=4)
        val_label = ctk.CTkLabel(parent, text=f"{val:.2f}")
        val_label.grid(row=row, column=2, padx=5)
        slider.configure(command=lambda v, lbl=val_label: lbl.configure(text=f"{float(v):.2f}"))
        self._entries[f"{section}.{key}"] = var
        return row + 1

    def _spin_row(self, parent, row, label, section, key, from_, to):
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=4)
        val = int(self.settings.get(section, {}).get(key, from_))
        var = ctk.IntVar(value=val)
        spin = ctk.CTkEntry(parent, width=80)
        spin.insert(0, str(val))
        spin.grid(row=row, column=1, sticky="w", padx=10, pady=4)
        self._entries[f"{section}.{key}"] = spin
        return row + 1

    def _logo_row(self, parent, row):
        ctk.CTkLabel(parent, text="App Logo").grid(row=row, column=0, sticky="nw", padx=10, pady=4)
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=1, sticky="ew", padx=10, pady=4)

        self.logo_preview = ctk.CTkLabel(frame, text="No logo")
        self.logo_preview.pack(side="left", padx=(0, 10))
        logo_img = load_logo_image((64, 64))
        if logo_img:
            self.logo_preview.configure(image=logo_img, text="")

        self.logo_path_entry = ctk.CTkEntry(frame, width=250)
        self.logo_path_entry.insert(0, self.settings.get("logo_path", "assets/logo.png"))
        self.logo_path_entry.pack(side="left", padx=5)
        ctk.CTkButton(frame, text="Browse", width=80, command=self.browse_logo).pack(side="left")
        return row + 1

    def browse_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.ico")])
        if path:
            rel = os.path.relpath(path, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.logo_path_entry.delete(0, "end")
            self.logo_path_entry.insert(0, rel)
            img = Image.open(path).resize((64, 64))
            self.logo_preview.configure(image=ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64)), text="")

    def browse_export(self):
        path = filedialog.askdirectory()
        if path:
            self.export_path.delete(0, "end")
            self.export_path.insert(0, path)

    def test_fingerprint(self):
        ok = fingerprint_module.connect()
        self.fp_status.configure(
            text="Connected to R307 on " + self.fp_port.get() if ok else fingerprint_module.last_error,
            text_color=("green", "#2ecc71") if ok else ("red", "#e74c3c"),
        )

    def test_scan(self):
        ok, msg = fingerprint_module.test_scan()
        self.fp_status.configure(text=msg, text_color=("green", "#2ecc71") if ok else ("red", "#e74c3c"))

    def save(self):
        self.settings["app_name"] = self._entries["app_name"].get()
        self.settings["institution"] = self._entries["institution"].get()
        self.settings["logo_path"] = self.logo_path_entry.get()

        for key, var in self.method_vars.items():
            self.settings["methods"][key] = var.get()

        self.settings["face"]["match_threshold"] = float(self._entries["face.match_threshold"].get())
        self.settings["face"]["camera_index"] = int(self._entries["face.camera_index"].get())

        self.settings["scanner"]["camera_index"] = int(self._entries["scanner.camera_index"].get())
        self.settings["scanner"]["beep_on_success"] = self.scanner_beep.get()

        self.settings["fingerprint"]["enabled"] = self.fp_enabled.get()
        self.settings["fingerprint"]["port"] = self.fp_port.get()
        self.settings["fingerprint"]["scan_timeout_sec"] = int(self._entries["fingerprint.scan_timeout_sec"].get())

        self.settings["reports"]["export_path"] = self.export_path.get()

        save_settings(self.settings)
        messagebox.showinfo("Settings", "Settings saved successfully.")
        if self.on_settings_saved:
            self.on_settings_saved()

    def reset(self):
        self.settings = reset_settings()
        messagebox.showinfo("Settings", "Settings reset to defaults. Reopen Settings to see changes.")
