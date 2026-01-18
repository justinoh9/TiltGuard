# TiltGuard
A Windows-first desktop companion that interrupts League of Legends launch/queue habits with friction, reflection, and session logging — helping you regain control before you press Play.

## Why
Many players don’t want to “quit gaming forever.” They want control:
- Stop tilt / rage-queue loops
- Reduce time spent without relying on willpower
- Protect sleep, grades, gym consistency, and mental bandwidth

TiltGuard is designed to intervene at the moment of relapse: when the game is about to start.

## Core Concept
When TiltGuard detects the League client launching, it displays an interruption modal that:
1. Shows simple stats (today/this week playtime)
2. Shows your personal reason for cutting back
3. Forces a choice with friction:
   - **Delay 15 minutes** (blocks League from launching during the delay)
   - **Play anyway** (override is allowed, but recorded)

## Features (Planned)
### V1 (Local-first)
- Detect League of Legends processes on Windows
- Interruption modal on launch
- Delay option that prevents launch for N minutes
- Session logging (start time, end time, overrides, delays)
- System tray icon + basic settings
- Local data storage (SQLite)

### V2 (Accountability add-on)
- Optional weekly summary report
- Optional accountability partner email/share link
- Simple web dashboard (sync logs)

## Non-Goals
- No shame / guilt messaging
- No “permanent ban” behavior (override is always possible)
- No social feed or chat in early versions

## Tech Stack (Planned)
- Python 3.11+
- PySide6 (Qt) for UI (modal, tray, settings)
- psutil for process detection
- pywin32 for Windows integration
- sqlite3 for local persistence
- PyInstaller for packaging

## Installation (Dev)
> Coming soon. Initial focus is getting the first working prototype.

### Requirements
- Windows 10/11
- Python 3.11+

### Setup (planned)
```bash
git clone https://github.com/<your-username>/tiltguard.git
cd tiltguard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
