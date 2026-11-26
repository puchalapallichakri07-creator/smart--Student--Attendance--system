"""R307 fingerprint sensor integration (COM3 default)."""

from core import database
from core.settings_manager import load_settings


class FingerprintModule:
    def __init__(self):
        self._sensor = None
        self._connected = False
        self._last_error = ""

    @property
    def last_error(self):
        return self._last_error

    @property
    def is_connected(self):
        return self._connected

    def _get_config(self):
        settings = load_settings()
        fp = settings.get("fingerprint", {})
        return {
            "port": fp.get("port", "COM3"),
            "baud_rate": fp.get("baud_rate", 57600),
            "address": fp.get("address", 0xFFFFFFFF),
            "password": fp.get("password", 0),
            "timeout": fp.get("scan_timeout_sec", 10),
            "enabled": fp.get("enabled", True),
        }

    def connect(self):
        self._last_error = ""
        config = self._get_config()
        if not config["enabled"]:
            self._last_error = "Fingerprint is disabled in settings."
            self._connected = False
            return False

        try:
            from pyfingerprint.pyfingerprint import PyFingerprint
        except ImportError:
            self._last_error = "pyfingerprint not installed. Run: pip install pyfingerprint pyserial"
            self._connected = False
            return False

        try:
            self._sensor = PyFingerprint(config["port"], config["baud_rate"], config["address"], config["password"])
            if not self._sensor.verifyPassword():
                raise ValueError("Sensor password verification failed.")
            self._connected = True
            return True
        except Exception as exc:
            self._sensor = None
            self._connected = False
            self._last_error = f"Cannot connect to R307 on {config['port']}: {exc}"
            return False

    def disconnect(self):
        self._sensor = None
        self._connected = False

    def test_scan(self):
        if not self._connected and not self.connect():
            return False, self._last_error

        try:
            self._sensor.convertImage(0x01)
            result = self._sensor.searchTemplate()
            position = result[0]
            if position >= 0:
                return True, f"Template found at position {position}"
            return True, "Scan OK — no matching template (place enrolled finger to match)"
        except Exception as exc:
            self._last_error = str(exc)
            return False, self._last_error

    def enroll(self, roll_no, name):
        if not self._connected and not self.connect():
            return False, self._last_error

        try:
            self._sensor.readImage()
            self._sensor.convertImage(0x01)
            self._sensor.createTemplate()
            position = self._sensor.storeTemplate()

            char = self._sensor.downloadCharacteristics(0x01)
            template = bytes(char) if char else b""

            existing = database.get_student(roll_no)
            if existing:
                database.update_student_fingerprint(roll_no, template, position)
            else:
                database.add_student(roll_no, name, fingerprint_template=template, fingerprint_id=position)

            return True, f"Fingerprint enrolled for {roll_no} - {name} (slot {position})"
        except Exception as exc:
            self._last_error = str(exc)
            return False, f"Enrollment failed: {exc}"

    def verify_and_match(self):
        if not self._connected and not self.connect():
            return None, None, self._last_error

        try:
            self._sensor.convertImage(0x02)
            result = self._sensor.searchTemplate()
            position = result[0]
            accuracy = result[1]

            if position == -1:
                return None, None, "No match found."

            for roll_no, name, _, fp_id in database.get_students_with_fingerprint():
                if fp_id == position:
                    return roll_no, name, f"Matched {name} (accuracy {accuracy})"

            return None, None, f"Match at slot {position} but no student linked."
        except Exception as exc:
            self._last_error = str(exc)
            return None, None, self._last_error


fingerprint_module = FingerprintModule()
