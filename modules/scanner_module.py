"""QR / barcode scanner using webcam."""

import winsound

import cv2

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

from core.settings_manager import load_settings
from modules.qr_module import parse_qr_data


def get_camera_index():
    settings = load_settings()
    return settings.get("scanner", {}).get("camera_index", 0)


def beep_on_success():
    settings = load_settings()
    if settings.get("scanner", {}).get("beep_on_success", True):
        try:
            winsound.Beep(1000, 200)
        except RuntimeError:
            pass


def decode_frame(frame):
    if pyzbar is None:
        return []

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    decoded = pyzbar.decode(rgb)
    results = []
    for item in decoded:
        try:
            text = item.data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        roll_no, name = parse_qr_data(text)
        if roll_no:
            results.append((roll_no, name, text, item.rect))
    return results


def draw_results(frame, results):
    for roll_no, name, _, rect in results:
        x, y, w, h = rect.left, rect.top, rect.width, rect.height
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{roll_no} - {name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame
