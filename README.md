# CAMPUS IQ — Smart Campus Operations

A modern Python desktop application for managing campus facilities, room bookings, equipment assets, maintenance requests, energy records, notifications and operational reports.

## Run the application
```powershell
cd campus_iq
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

**Note:** Tkinter is included with standard Windows Python. Do not try to install it with pip. CustomTkinter and the other third-party packages are installed from `requirements.txt`.

See [campus_iq/README.md](campus_iq/README.md) for demo accounts, module details, role permissions, tests and limitations.

## Project status
The `feature/campus-iq` branch contains the development version. Review the pull request before merging it into `main`.
