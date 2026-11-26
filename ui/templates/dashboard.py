"""Dashboard with today's stats."""

import customtkinter as ctk

from core.attendance_service import AttendanceService
from ui.components.base_frame import BaseFrame


class DashboardView(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, title="Dashboard", subtitle="Overview of student attendance", **kwargs)
        self.stats_frame = ctk.CTkFrame(self.content)
        self.stats_frame.grid(row=0, column=0, sticky="nsew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.stats_frame.grid_rowconfigure((0, 1), weight=1)

        self.total_label = self._stat_card(self.stats_frame, "Total Students", "0", 0, 0)
        self.present_label = self._stat_card(self.stats_frame, "Present Today", "0", 0, 1)
        self.absent_label = self._stat_card(self.stats_frame, "Absent Today", "0", 0, 2)

        self.list_frame = ctk.CTkFrame(self.stats_frame)
        self.list_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.list_frame, text="Today's Attendance", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )
        self.records_box = ctk.CTkTextbox(self.list_frame, height=200)
        self.records_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        refresh_btn = ctk.CTkButton(self.stats_frame, text="Refresh", command=self.refresh)
        refresh_btn.grid(row=2, column=2, sticky="e", padx=10, pady=10)

        self.refresh()

    def _stat_card(self, parent, title, value, row, col):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color="gray").pack(pady=(15, 5))
        val_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"))
        val_label.pack(pady=(0, 15))
        return val_label

    def refresh(self):
        stats = AttendanceService.get_dashboard_stats()
        total = stats["total_students"]
        present = stats["present_today"]
        absent = max(total - present, 0)

        self.total_label.configure(text=str(total))
        self.present_label.configure(text=str(present))
        self.absent_label.configure(text=str(absent))

        self.records_box.delete("1.0", "end")
        records = stats["today_records"]
        if not records:
            self.records_box.insert("end", "No attendance marked yet today.\n")
        else:
            for roll_no, name, time_str, method in records:
                self.records_box.insert("end", f"{roll_no} | {name} | {time_str} | {method}\n")
