"""Face recognition enrollment and attendance."""

import cv2
import face_recognition
import numpy as np

from core import database
from core.settings_manager import load_settings


def get_threshold():
    return load_settings().get("face", {}).get("match_threshold", 0.6)


def get_camera_index():
    return load_settings().get("face", {}).get("camera_index", 0)


def capture_face_encoding(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb_frame)
    if len(locations) != 1:
        return None, "Ensure exactly ONE face is visible."
    encoding = face_recognition.face_encodings(rgb_frame, locations)[0]
    return encoding, None


def enroll_face(roll_no, name, frame):
    encoding, error = capture_face_encoding(frame)
    if error:
        return False, error

    existing = database.get_student(roll_no)
    if existing:
        database.update_student_face(roll_no, encoding)
        return True, f"Face updated for {roll_no} - {name}"
    database.add_student(roll_no, name, encoding=encoding)
    return True, f"Face enrolled: {roll_no} - {name}"


def process_frame(frame, known_encodings, known_roll_nos, known_names, already_marked, on_marked):
    threshold = get_threshold()
    small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, locations)
    labels = []

    for (top, right, bottom, left), face_encoding in zip(locations, encodings):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_index = int(np.argmin(distances))
        best_distance = distances[best_index]

        if best_distance < threshold:
            roll_no = known_roll_nos[best_index]
            name = known_names[best_index]
            label = name
            if roll_no not in already_marked:
                already_marked.add(roll_no)
                on_marked(roll_no, name, "face")
        else:
            label = "Unknown"

        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        color = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        labels.append(label)

    return frame, labels
