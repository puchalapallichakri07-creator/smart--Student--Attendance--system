"""Student enrollment view — face, QR, fingerprint."""

import threading
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

from core import database
from modules import face_module, qr_module
from modules import face_module, qr_module
from modules.fingerprint_module import fingerprint_module
from ui.components.base_frame import BaseFrame


class EnrollView(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, title="Enroll Student", subtitle="Register students using face, QR, or fingerprint", **kwargs)

        form = ctk.CTkFrame(self.content)
        form.grid(row=0, column=0, sticky="nsew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Roll Number").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.roll_entry = ctk.CTkEntry(form, placeholder_text="e.g. 101")
        self.roll_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=8)

        ctk.CTkLabel(form, text="Student Name").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.name_entry = ctk.CTkEntry(form, placeholder_text="Full name")
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=8)

        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        btn_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(btn_frame, text="Enroll Face", command=self.enroll_face).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Generate QR", command=self.enroll_qr).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Enroll Fingerprint", command=self.enroll_fingerprint).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="Enroll All Methods", command=self.enroll_all).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.status_label = ctk.CTkLabel(form, text="", wraplength=600, justify="left")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.qr_preview = ctk.CTkLabel(form, text="QR preview will appear here")
        self.qr_preview.grid(row=4, column=0, columnspan=2, pady=10)

        self.camera_label = ctk.CTkLabel(form, text="")
        self.camera_label.grid(row=5, column=0, columnspan=2, pady=5)

        self._camera_running = False
        self._video = None

    def _get_inputs(self):
        roll_no = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()
        if not roll_no or not name:
            messagebox.showwarning("Missing Info", "Enter roll number and name first.")
            return None, None
        return roll_no, name

    def _set_status(self, message):
        self.status_label.configure(text=message)

    def enroll_qr(self):
        roll_no, name = self._get_inputs()
        if not roll_no:
            return
        ok, msg, path = qr_module.enroll_qr(roll_no, name)
        self._set_status(msg)
        if ok and path:
            img = Image.open(path)
            img = img.resize((180, 180))
            self.qr_preview.configure(image=ctk.CTkImage(light_image=img, dark_image=img, size=(180, 180)), text="")

    def enroll_fingerprint(self):
        roll_no, name = self._get_inputs()
        if not roll_no:
            return
        self._set_status("Place finger on R307 sensor...")
        threading.Thread(target=self._fingerprint_enroll_thread, args=(roll_no, name), daemon=True).start()

    def _fingerprint_enroll_thread(self, roll_no, name):
        ok, msg = fingerprint_module.enroll(roll_no, name)
        self.after(0, lambda: self._set_status(msg if ok else f"Error: {msg}"))

    def enroll_face(self):
        roll_no, name = self._get_inputs()
        if not roll_no:
            return
        self._open_face_capture(roll_no, name)

    def enroll_all(self):
        roll_no, name = self._get_inputs()
        if not roll_no:
            return
        self.enroll_qr()
        self.enroll_fingerprint()
        self._open_face_capture(roll_no, name)

    def _open_face_capture(self, roll_no, name):
        if self._camera_running:
            return
        self._camera_running = True
        self._set_status("Look at the camera. Press SPACE to capture, ESC to cancel.")

        win = tk.Toplevel(self)
        win.title("Face Enrollment")
        win.geometry("680x520")
        label = tk.Label(win)
        label.pack()

        video = cv2.VideoCapture(face_module.get_camera_index())

        def update_frame():
            if not self._camera_running:
                return
            ret, frame = video.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb).resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.configure(image=imgtk)
            win.after(30, update_frame)

        def on_key(event):
            if event.keysym == "Escape":
                cleanup()
            elif event.keysym == "space":
                ret, frame = video.read()
                if ret:
                    ok, msg = face_module.enroll_face(roll_no, name, frame)
                    self._set_status(msg)
                    if ok:
                        cleanup()

        def cleanup():
            self._camera_running = False
            video.release()
            win.destroy()

        win.bind("<Key>", on_key)
        update_frame()
