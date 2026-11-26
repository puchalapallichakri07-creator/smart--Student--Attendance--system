"""Unified attendance marking service."""

from core import database


class AttendanceService:
    @staticmethod
    def mark_present(roll_no, name, method):
        return database.mark_attendance(roll_no, name, method)

    @staticmethod
    def get_dashboard_stats():
        return {
            "total_students": database.student_count(),
            "present_today": database.today_present_count(),
            "today_records": database.get_today_attendance(),
        }

    @staticmethod
    def lookup_by_qr_payload(payload):
        student = database.get_student_by_qr(payload)
        if student:
            return student[0], student[1]
        return None, None
