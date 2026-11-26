"""QR code generation and validation."""

import json
import os

import qrcode

from core import database
from core.settings_manager import resolve_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QR_DIR = os.path.join(BASE_DIR, "assets", "qrcodes")


def build_qr_payload(roll_no, name):
    return json.dumps({"roll_no": roll_no, "name": name})


def generate_qr(roll_no, name):
    os.makedirs(QR_DIR, exist_ok=True)
    payload = build_qr_payload(roll_no, name)
    path = os.path.join(QR_DIR, f"{roll_no}.png")

    img = qrcode.make(payload)
    img.save(path)
    return payload, path


def enroll_qr(roll_no, name):
    payload, path = generate_qr(roll_no, name)
    existing = database.get_student(roll_no)
    if existing:
        database.update_student_qr(roll_no, payload)
        return True, f"QR updated for {roll_no}", path
    database.add_student(roll_no, name, qr_data=payload)
    return True, f"QR enrolled: {roll_no} - {name}", path


def parse_qr_data(raw_data):
    try:
        data = json.loads(raw_data)
        roll_no = data.get("roll_no")
        name = data.get("name")
        if roll_no and name:
            return roll_no, name
    except (json.JSONDecodeError, TypeError):
        pass

    student = database.get_student_by_qr(raw_data)
    if student:
        return student[0], student[1]

    student = database.get_student(raw_data)
    if student:
        return student[0], student[1]

    return None, None


def get_qr_image_path(roll_no):
    path = resolve_path(os.path.join("assets", "qrcodes", f"{roll_no}.png"))
    return path if os.path.exists(path) else None
