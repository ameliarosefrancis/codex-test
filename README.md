AmeliaRose Toolkit GUI
======================

What
----
This workspace contains a small Tkinter GUI (`app_gui.py`) that launches and monitors the project's helper scripts (order intake, pricing, stock checks, etc.). It lists available modules, can run them in the foreground while capturing output, or start them in the background.

Requirements
------------
- Python 3.8+ (Windows)
- Tkinter (usually included with standard Python on Windows)

Quick start
-----------
From the project root run:

```bash
python app_gui.py
```

Or double-click `StartToolkit.bat` on Windows to launch the toolkit if configured.

Alternatively, use the packaged executable `Toolkit V1.11.exe` for a standalone application.

Features
--------
- "Run (capture output)": runs the script and shows stdout/stderr in the GUI.
- "Run (background)": starts the script in a separate process.
- "Open Script...": add local scripts to the list.
- Quick access buttons for common CSV log files.
- Stock tools menu with shopping list options.
- Documentation submenu in Help menu.
- About dialog with company information.
- Dark mode toggle.
- Loads `AmeliaRoseIcon.ico` from the project root when available.

Menu Structure
--------------
- File: Exit
- Stock: Open Shopping List, Print Shopping List
- Options: Dark Mode
- Help: Documentation (submenus for each README), About

Troubleshooting
---------------
- If a script fails to run, check the Output pane for error text.
- Ensure the script you run is compatible with being executed as a standalone Python program.
- If the icon doesn't appear on non-Windows platforms, that is expected (iconbitmap is Windows-specific).
- For the executable, ensure all required files (CSV logs, shopping list) are in the same directory as the exe.

Files
-----
- `app_gui.py` — the GUI launcher 
- `launcher.py` — CLI menu launcher
- `Toolkit V1.11.exe` — standalone executable version (usally few versions behind the app_gui)
- `AmeliaRoseIcon.ico` — application icon

License / Notes
----------------
This README is a quick guide. Tell me if you want a longer README, packaged executable, or OS-specific shortcuts.
