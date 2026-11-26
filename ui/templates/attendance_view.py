"""Mark attendance using face, QR scanner, or fingerprint."""

import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

from core import database
from core.attendance_service import AttendanceService
from modules import face_module, scanner_module
from modules import face_module, scanner_module
from modules.fingerprint_module import fingerprint_module
from ui.components.base_frame import BaseFrame


class AttendanceView(BaseFrame):
    METHODS = [
        ("Face Recognition", "face"),
        ("QR Scanner", "scanner"),
        ("Fingerprint (R307)", "fingerprint"),
    ]

    def __init__(self, master, on_attendance_marked=None, **kwargs):
        super().__init__(master, title="Mark Attendance", subtitle="Choose a method and start scanning", **kwargs)
        self.on_attendance_marked = on_attendance_marked
        self._running = False
        self._already_marked = set()

        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.method_var = ctk.StringVar(value="face")
        method_frame = ctk.CTkFrame(top)
        method_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        for i, (label, value) in enumerate(self.METHODS):
            ctk.CTkRadioButton(method_frame, text=label, variable=self.method_var, value=value).grid(
                row=0, column=i, padx=15, pady=10
            )

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew")
        ctk.CTkButton(btn_frame, text="Start", command=self.start).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Stop", command=self.stop, fg_color="gray").pack(side="left", padx=5)

        self.status = ctk.CTkLabel(top, text="Select a method and click Start.", wraplength=700, justify="left")
        self.status.grid(row=2, column=0, sticky="w", pady=10)

        self.log_box = ctk.CTkTextbox(self.content, height=120)
        self.log_box.grid(row=1, column=0, sticky="ew", pady=10)

        self.camera_label = ctk.CTkLabel(self.content, text="Camera preview opens in a separate window")
        self.camera_label.grid(row=2, column=0, sticky="w")

    def _log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.status.configure(text=message)

    def _handle_mark(self, roll_no, name, method):
        newly = AttendanceService.mark_present(roll_no, name, method)
        if newly:
            self._log(f"Present: {roll_no} - {name} ({method})")
        else:
            self._log(f"Already marked today: {roll_no} - {name}")
        if self.on_attendance_marked:
            self.on_attendance_marked()

    def start(self):
        method = self.method_var.get()
        self._already_marked.clear()
        if method == "fingerprint":
            self._start_fingerprint()
        else:
            self._start_camera(method)

    def stop(self):
        self._running = False

    def _start_fingerprint(self):
        self._running = True
        self._log("Place finger on R307 sensor...")
        threading.Thread(target=self._fingerprint_loop, daemon=True).start()

    def _fingerprint_loop(self):
        while self._running:
            roll_no, name, msg = fingerprint_module.verify_and_match()
            if roll_no and roll_no not in self._already_marked:
                self._already_marked.add(roll_no)
                self.after(0, lambda r=roll_no, n=name: self._handle_mark(r, n, "fingerprint"))
                self.after(0, lambda m=msg: self._log(m))
            elif msg and "No match" not in msg:
                self.after(0, lambda m=msg: self.status.configure(text=m))
            threading.Event().wait(1.5)

    def _start_camera(self, method):
        if self._running:
            return
        self._running = True

        win = tk.Toplevel(self)
        win.title("Attendance - Press Q to stop")
        label = tk.Label(win)
        label.pack()

        camera_index = (
            face_module.get_camera_index()
            if method == "face"
            else scanner_module.get_camera_index()
        )
        video = cv2.VideoCapture(camera_index)

        students = database.get_students_with_face()
        known_encodings = [s[2] for s in students]
        known_roll_nos = [s[0] for s in students]
        known_names = [s[1] for s in students]

        def loop():
            if not self._running:
                video.release()
                win.destroy()
                return

            ret, frame = video.read()
            if ret:
                if method == "face":
                    frame, _ = face_module.process_frame(
                        frame,
                        known_encodings,
                        known_roll_nos,
                        known_names,
                        self._already_marked,
                        lambda r, n, m: self.after(0, lambda: self._handle_mark(r, n, m)),
                    )
                else:
                    results = scanner_module.decode_frame(frame)
                    frame = scanner_module.draw_results(frame, results)
                    for roll_no, name, _, _ in results:
                        if roll_no not in self._already_marked:
                            self._already_marked.add(roll_no)
                            scanner_module.beep_on_success()
                            self.after(0, lambda r=roll_no, n=name: self._handle_mark(r, n, "scanner"))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb).resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.configure(image=imgtk)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self._running = False

            win.after(30, loop)

        win.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "_running", False), win.destroy()))
        loop()
