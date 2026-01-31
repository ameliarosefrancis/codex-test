# Virtual Environment Setup Guide

## What is a Virtual Environment?

A Python virtual environment (venv) is an isolated Python installation that:
- Keeps project dependencies separate from system Python
- Prevents version conflicts between projects
- Makes projects reproducible across different systems
- Allows pinning specific package versions

## Current Status

**Issue Found:** The `venv/` folder in this project is configured for Linux (Debian).

Since this project runs on Windows, we need to either:
1. Delete the old venv and create a new Windows-compatible one
2. Use the system Python directly

## Option A: Create a Windows Virtual Environment (Recommended)

### Using PowerShell

```powershell
# 1. Navigate to project directory
cd "C:\Users\ameli\Documents\AmeliaRoseCo\AmeliaRoseCo Toolkit\AB V1.11"

# 2. Remove old Linux venv (if desired)
Remove-Item -Recurse -Force venv

# 3. Create new venv
python -m venv venv

# 4. Activate venv
.\venv\Scripts\Activate.ps1

# Note: If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. Verify Python
python --version

# 6. Install dependencies (optional - no external dependencies needed)
pip install -r requirements.txt

# 7. Run application
python app_gui.py

# 8. Deactivate when done
deactivate
```

### Using Command Prompt (CMD)

```batch
REM 1. Navigate to project directory
cd "C:\Users\ameli\Documents\AmeliaRoseCo\AmeliaRoseCo Toolkit\AB V1.11"

REM 2. Remove old Linux venv (if desired)
rmdir /s /q venv

REM 3. Create new venv
python -m venv venv

REM 4. Activate venv
venv\Scripts\activate.bat

REM 5. Verify Python
python --version

REM 6. Install dependencies
pip install -r requirements.txt

REM 7. Run application
python app_gui.py

REM 8. Deactivate when done
deactivate
```

## Option B: Use Pre-Made Launch Scripts

We've created convenient launch scripts that automatically activate the venv:

### PowerShell Method
```powershell
.\run_with_venv.ps1
```

### Batch Method
```batch
run_with_venv.bat
```

These scripts will:
1. Check if venv exists
2. Activate it automatically
3. Launch the application
4. Clean up on exit

## Option C: Run Without Virtual Environment

If you prefer not to use venv, simply run:

```powershell
python app_gui.py
```

This works fine since the project has no external dependencies.

## What's in requirements.txt?

This project uses only Python's standard library:
- tkinter (GUI)
- csv, json (data)
- zipfile (archives)
- subprocess, threading (execution)
- logging, pathlib (utilities)

All of these come with Python, so there are no packages to install.

## Why Use venv Anyway?

Even though we don't have external dependencies, venv is useful for:
- **Future-proofing**: Easy to add packages later
- **Environment Consistency**: Same Python across machines
- **Professional Practice**: Industry standard
- **CI/CD Ready**: Docker and automation tools expect it
- **Separation**: Keeps project Python isolated
- **Reproducibility**: Can recreate exact environment

## Folder Structure

After setting up venv, you'll have:

```
venv/
├── Scripts/              (executables)
│   ├── python.exe        (Python interpreter)
│   ├── pip.exe           (Package installer)
│   ├── Activate.ps1      (PowerShell activation)
│   └── activate.bat      (CMD activation)
├── Lib/                  (Python libraries)
├── Include/              (Header files)
├── pyvenv.cfg            (Configuration)
└── ...
```

## Troubleshooting

### Issue: "python: command not found"
**Solution:** Python is not in your PATH. Use the full path:
```powershell
C:\Python311\python.exe -m venv venv
```

### Issue: "Execution Policy" error
**Solution:** Allow script execution (PowerShell):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Old Linux venv won't activate
**Solution:** Delete and recreate it:
```powershell
Remove-Item -Recurse -Force venv
python -m venv venv
```

### Issue: "ModuleNotFoundError: No module named 'tkinter'"
**Solution:** Tkinter might not be installed. Reinstall Python and check "tcl/tk and IDLE" during installation.

## Git and venv

The `.gitignore` already correctly ignores venv:
```gitignore
venv/
lib/
bin/
include/
```

So venv won't be committed to git (good practice!).

## Next Steps

1. Choose an option above (A, B, or C)
2. Verify Python works: `python --version`
3. Launch the app: `python app_gui.py`
4. Test that windows center correctly (new feature!)
5. Test DMARC ZIP upload feature (new feature!)

---

**Last Updated:** January 31, 2026  
**Project:** AmeliaRoseCo Toolkit v1.20
