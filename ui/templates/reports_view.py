"""Export attendance reports to Excel."""

import os
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
import pandas as pd

from core import database
from core.settings_manager import load_settings, resolve_path
from ui.components.base_frame import BaseFrame


class ReportsView(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, title="Reports", subtitle="View and export attendance records", **kwargs)

        self.content.grid_rowconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Export to Excel", command=self.export_excel).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh).pack(side="left", padx=5)

        self.records_box = ctk.CTkTextbox(self.content)
        self.records_box.grid(row=1, column=0, sticky="nsew")

        self.refresh()

    def refresh(self):
        self.records_box.delete("1.0", "end")
        rows = database.get_all_attendance()
        if not rows:
            self.records_box.insert("end", "No attendance records yet.\n")
            return
        self.records_box.insert("end", f"{'Roll No':<12} {'Name':<20} {'Date':<12} {'Time':<10} {'Method'}\n")
        self.records_box.insert("end", "-" * 70 + "\n")
        for roll_no, name, date, time_str, method in rows[:200]:
            self.records_box.insert("end", f"{roll_no:<12} {name:<20} {date:<12} {time_str:<10} {method}\n")

    def export_excel(self):
        settings = load_settings()
        export_dir = resolve_path(settings.get("reports", {}).get("export_path", "reports"))
        os.makedirs(export_dir, exist_ok=True)

        rows = database.get_all_attendance()
        if not rows:
            messagebox.showinfo("Export", "No records to export.")
            return

        df = pd.DataFrame(rows, columns=["roll_no", "name", "date", "time", "method"])
        filename = os.path.join(export_dir, f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        df.to_excel(filename, index=False)
        messagebox.showinfo("Export Complete", f"Report saved to:\n{filename}")
        self.refresh()
