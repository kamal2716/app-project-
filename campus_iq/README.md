# CAMPUS IQ
### Smart Campus Operations & Resource Intelligence System

CAMPUS IQ is a Windows desktop application built with Python, CustomTkinter and SQLite. It brings campus facilities, bookings, assets, maintenance and energy records into one interface.

## Features
- Role-based sign-in for administrators, faculty, students, lab assistants and maintenance staff.
- Database-backed dashboard with campus metrics and maintenance activity.
- Facility directory and reservation requests with overlap and capacity validation.
- Equipment asset register and repair-condition tracking.
- Maintenance ticket workflow with rule-based priority suggestions.
- Building-level energy records and consumption summaries.
- CSV, Excel and PDF report exports.
- Automatic SQLite database creation with sample data.

## Quick start (Windows)
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:
   `py -m venv .venv`
   `.venv\\Scripts\\activate`
4. Install packages:
   `python -m pip install -r requirements.txt`
5. Run:
   `python main.py`

## Demo accounts
| Role | Username | Password |
|---|---|---|
| Administrator | admin | Admin@123 |
| Faculty | faculty | Faculty@123 |
| Student | student | Student@123 |
| Lab Assistant | labassistant | Lab@123 |
| Maintenance Staff | maintenance | Fix@123 |

These credentials are for local demonstration only. Change them before using real institutional data. Production deployment should use per-user random salts, a password-reset flow, and database access controls.

## Architecture
- `database/`: SQLite schema, connection handling and demonstration seed data.
- `services/`: authentication, bookings, assets, maintenance and analytics.
- `ui/`: CustomTkinter login, navigation, reusable cards and application pages.
- `utils/`: report export utilities.
- `data/`: created automatically for the SQLite database.
- `exports/`: generated reports.

## Data integrity
- Booking requests reject past dates, invalid time ranges, capacity overflows and overlapping requests.
- Energy records preserve a source label (Manual, Demo, etc.).
- Maintenance priority is a transparent rule-based suggestion; an authorized administrator remains responsible for final decisions.
- Sample/demo data is clearly identified.

## Testing and syntax checks
From this folder:
`python -m unittest discover -s tests -v`
`python -m compileall -q .`

## Current MVP scope
Implemented: login, dashboard, facility directory, booking request, asset registry, maintenance workflow, energy records and PDF/Excel/CSV report export.

Planned extensions: QR code workflows, full administration CRUD, richer chart visualizations, notification delivery, department-specific permissions and connected IoT energy meters. The current energy screen uses stored manual/demo readings and does not claim live IoT integration.
