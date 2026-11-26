# Smart Student Attendance

Windows desktop app for student attendance using **QR Code**, **Face Recognition**, **Fingerprint (R307/COM3)**, and **Scanner**.

## Features

- **Dashboard** — today's present/absent counts and live attendance log
- **Enroll** — register students via face, QR, fingerprint, or all methods
- **Mark Attendance** — face camera, QR scanner, or R307 fingerprint
- **Reports** — view history and export to Excel
- **Settings** — toggle methods, thresholds, COM port, logo, export path

## Quick Start (Windows)

1. Install [Python 3.10+](https://www.python.org/downloads/) — enable **Add to PATH**
2. Open this folder and double-click **`setup.bat`**
3. Double-click **`run.bat`** to launch the app

Or from terminal:

```powershell
cd C:\Users\Lenovo\smart-attendance
python -m pip install -r requirements.txt
python main.py
```

## Fingerprint (R307)

- Connect R307 module to **COM3** (change in Settings if needed)
- Use **Settings → Test Connection** and **Test Scan**
- Requires: `pyfingerprint`, `pyserial`

## Build .exe

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/logo.ico --name=SmartAttendance main.py
```

Output: `dist/SmartAttendance.exe`

## Project Structure

```
smart-attendance/
├── main.py                 # Entry point
├── config/settings.json    # App settings
├── assets/logo.png         # App logo
├── core/                   # Database, settings, service
├── modules/                # Face, QR, scanner, fingerprint
└── ui/                     # CustomTkinter windows
```

## Notes

- **pyzbar** on Windows may need [ZBar DLLs](https://github.com/NaturalHistoryMuseum/pyzbar) in PATH for QR scanning.
- **face_recognition** requires CMake and Visual Studio Build Tools on first install.
- Fingerprint works when R307 hardware is connected; other methods work without it.
