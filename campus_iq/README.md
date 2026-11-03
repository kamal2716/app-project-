# CAMPUS IQ
### Smart Campus Operations & Resource Intelligence System

CAMPUS IQ is a Windows desktop application built with Python, CustomTkinter and SQLite. It centralizes campus facilities, bookings, equipment, maintenance tickets, energy records, notifications and reports.

## Features
- Role-aware sign-in for administrators, faculty, students, lab assistants and maintenance staff.
- Dashboard with live database counts and recent maintenance activity.
- Facility directory; administrators can register facilities.
- Booking requests with date/time validation, capacity checks, overlap prevention, administrator approval/rejection and requester notifications.
- Asset register with condition tracking.
- Maintenance reporting for students and staff, role-limited ticket visibility, assignment/status workflow and requester notifications.
- Energy summaries and monthly chart from stored meter records. Demo readings are labelled; no live IoT integration is claimed.
- In-app notification centre.
- CSV, Excel and PDF exports saved to the exact path selected in the save dialog.
- SQLite database creation and legacy demo-data migration.

## Windows setup
Use Python 3.10 or newer (Python 3.13 is supported by the dependency set).
```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```
Do not run `pip install tkinter`: Tkinter is part of the standard Windows Python installation. CustomTkinter is installed through requirements.txt.

## Demo accounts
| Role | Username | Password |
|---|---|---|
| Administrator | admin | Admin@123 |
| Faculty | faculty | Faculty@123 |
| Student | student | Student@123 |
| Lab Assistant | labassistant | Lab@123 |
| Maintenance Staff | maintenance | Fix@123 |

Demo passwords are for evaluation only. Change them before any real deployment. Password hashes use PBKDF2-HMAC-SHA256 with per-user random salts; legacy demo hashes are upgraded on successful sign-in.

## Role access
- Administrator: all modules, facility registration, booking approvals, maintenance workflow and reports.
- Faculty: dashboard, facilities, own booking requests, energy view and reports.
- Student: dashboard, facilities, own bookings, own maintenance reports and notifications.
- Lab Assistant: dashboard, facilities, asset register, maintenance reporting and notifications.
- Maintenance Staff: dashboard, facilities, maintenance queue, reports and notifications.

## Architecture
- `database/`: SQLite schema, connection handling, seed data and migrations.
- `services/`: authentication, bookings, assets, maintenance, notifications and analytics.
- `ui/`: CustomTkinter login, navigation, tables, forms and pages.
- `utils/`: report exporters.
- `data/`: automatically created SQLite database.
- `exports/`: available for generated project exports.

## Tests
```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
```
Tests cover demo authentication, per-user password salts, booking conflict/approval, maintenance status and notifications, and CSV export destination.

## Data and limitations
- Energy readings are manually stored demonstration records, not live smart-meter data.
- Priority is a transparent keyword-based suggestion, not an AI diagnosis.
- In-app notifications appear in the application; no email/SMS delivery is configured.
- This is an academic MVP, not a hardened production campus platform.
