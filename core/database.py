"""SQLite database operations for Smart Student Attendance."""

import os
import sqlite3
from datetime import datetime

import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "attendance.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            encoding BLOB,
            qr_data TEXT,
            fingerprint_template BLOB,
            fingerprint_id INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            method TEXT NOT NULL DEFAULT 'manual',
            UNIQUE(roll_no, date)
        )
        """
    )

    conn.commit()
    conn.close()


def add_student(roll_no, name, encoding=None, qr_data=None, fingerprint_template=None, fingerprint_id=None):
    conn = get_connection()
    cur = conn.cursor()
    encoding_bytes = encoding.tobytes() if encoding is not None else None
    cur.execute(
        """
        INSERT INTO students (roll_no, name, encoding, qr_data, fingerprint_template, fingerprint_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (roll_no, name, encoding_bytes, qr_data, fingerprint_template, fingerprint_id),
    )
    conn.commit()
    conn.close()


def update_student_face(roll_no, encoding):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET encoding = ? WHERE roll_no = ?",
        (encoding.tobytes(), roll_no),
    )
    conn.commit()
    conn.close()


def update_student_qr(roll_no, qr_data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE students SET qr_data = ? WHERE roll_no = ?", (qr_data, roll_no))
    conn.commit()
    conn.close()


def update_student_fingerprint(roll_no, template, fingerprint_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET fingerprint_template = ?, fingerprint_id = ? WHERE roll_no = ?",
        (template, fingerprint_id, roll_no),
    )
    conn.commit()
    conn.close()


def get_student(roll_no):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT roll_no, name, encoding, qr_data, fingerprint_template, fingerprint_id FROM students WHERE roll_no = ?",
        (roll_no,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_student_by_qr(qr_data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT roll_no, name, encoding, qr_data, fingerprint_template, fingerprint_id FROM students WHERE qr_data = ?",
        (qr_data,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT roll_no, name, encoding, qr_data, fingerprint_template, fingerprint_id FROM students ORDER BY roll_no"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_students_with_face():
    students = []
    for row in get_all_students():
        roll_no, name, encoding_bytes, _, _, _ = row
        if encoding_bytes:
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
            students.append((roll_no, name, encoding))
    return students


def get_students_with_fingerprint():
    students = []
    for row in get_all_students():
        roll_no, name, _, _, template, fp_id = row
        if template:
            students.append((roll_no, name, template, fp_id))
    return students


def student_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    count = cur.fetchone()[0]
    conn.close()
    return count


def mark_attendance(roll_no, name, method="manual"):
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    try:
        cur.execute(
            "INSERT INTO attendance (roll_no, name, date, time, method) VALUES (?, ?, ?, ?, ?)",
            (roll_no, name, today, now_time, method),
        )
        conn.commit()
        marked_new = True
    except sqlite3.IntegrityError:
        marked_new = False

    conn.close()
    return marked_new


def get_today_attendance():
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        "SELECT roll_no, name, time, method FROM attendance WHERE date = ? ORDER BY time",
        (today,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_attendance():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll_no, name, date, time, method FROM attendance ORDER BY date DESC, time DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def today_present_count():
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
    count = cur.fetchone()[0]
    conn.close()
    return count
