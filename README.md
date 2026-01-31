AmeliaRose Toolkit - Modern GUI Launcher
=========================================

**Version 1.20 | January 31, 2026**

What is This?
-------------
The AmeliaRoseCo Toolkit is a comprehensive business automation platform with a modern Tkinter GUI. It launches and monitors helper scripts for order processing, pricing, inventory management, customer follow-ups, and more.

**Key Features:**
- 🎨 Modern dark/light theme with persistent settings
- 📊 Real-time module output capture with color-coded logging
- 🔧 Built-in stock level and SKU management tools
- 🔐 DMARC security report processor with ZIP support
- 🖥️ Multi-monitor aware - all windows center on primary display
- ⚡ Thread-safe operation with concurrent task execution
- 📋 Professional error handling and comprehensive logging

Quick Start
-----------

### Option 1: Direct Python (Recommended for Development)
```bash
python app_gui.py
```

### Option 2: With Virtual Environment (Recommended for Deployment)
```bash
# First time only: Create virtual environment
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Run application
python app_gui.py
```

### Option 3: Using Pre-Made Launch Script
```bash
# PowerShell
.\run_with_venv.ps1

# Command Prompt
run_with_venv.bat
```

### Option 4: Executable (No Python Required)
```bash
Toolkit V1.11.exe
```

Requirements
------------
- **Python 3.10+** (Windows)
- **Tkinter** (included with standard Python on Windows)
- No external package dependencies

**Virtual Environment Setup:**
See [VENV_SETUP_GUIDE.md](VENV_SETUP_GUIDE.md) for comprehensive virtual environment instructions.

Features (Updated v1.20)
------------------------

### Core Features
- ✅ Module Launcher: Execute any configured script with output capture
- ✅ Real-time Output Panel: Color-coded stdout/stderr display
- ✅ Dark/Light Theme: Toggle with Ctrl+D, persistent across sessions
- ✅ Status Bar: Real-time operation feedback
- ✅ Keyboard Shortcuts: Ctrl+Q (exit), Ctrl+D (theme), Ctrl+L (open folder)

### Management Tools
- ✅ **Stock Level Editor**: Add/edit/delete inventory items (CSV-backed)
- ✅ **SKU Manager**: Manage product SKUs with materials and descriptions (JSON-backed)
- ✅ **DMARC Report Processor**: Upload and process DMARC reports with ZIP archive support

### Log Viewers
- ✅ Quick-access buttons for common logs
- ✅ View customer activity, pricing, maintenance, and stock history
- ✅ Open log folder directly from GUI

### Documentation
- ✅ Built-in documentation access
- ✅ Module-specific README files
- ✅ Keyboard shortcuts reference
- ✅ About dialog with company information

### New in v1.20 (January 31, 2026)
- 🆕 **Window Centering**: All dialogs now center on primary monitor (multi-monitor support)
- 🆕 **ZIP File Support**: DMARC processor accepts .zip archives with auto-extraction
- 🆕 **Enhanced Logging**: More detailed operation feedback
- 🆕 **Optimized JSON**: All config files validated and optimized
- 🆕 **Virtual Environment Setup**: Professional deployment ready

Menu Structure
--------------

```
File
├── 🔍 Open Working Directory
├── ⚙️ Settings
└── Exit (Ctrl+Q)

Tools
├── 📊 View Stock Levels
├── 📋 Edit SKUs
├── 🔐 Process DMARC Report
├── 📂 Open Shopping List
└── 🖨️ Print Shopping List

Logs
├── customer_log.csv
├── pricing_log.csv
├── maintenance_log.csv
├── stock_levels.csv
└── 📂 Open Logs Folder

Options
└── 🌙 Dark Mode (Ctrl+D)

Help
├── 📖 Documentation
│   ├── 📦 Order Intake & Prep
│   ├── 💰 Pricing Calculator
│   ├── 📊 Stock Level Checker
│   ├── 👥 Customer Follow-Up
│   ├── 🔧 Maintenance Reminders
│   └── 🔐 DMARC Report Parser
├── 📋 Keyboard Shortcuts
└── ℹ️ About
```

Modules
-------

The left panel displays available automation modules:

```
📦 Order Intake & Prep       - Process incoming orders and prep work
💰 Pricing Calculator         - Calculate product pricing
📊 Stock Level Checker        - Analyze inventory levels
📈 Profit Calculator          - Calculate profit margins
👥 Customer Follow-Up         - Send follow-up communications
🔧 Maintenance Reminders      - Schedule maintenance tasks
⚙️ Edit Stock Levels          - Manage inventory database
📋 Edit SKUs                  - Manage product SKUs
🔐 Process DMARC Report       - Process security reports
```

Advanced Features
-----------------

### DMARC Report Processing (New in v1.20)

Upload and automatically process DMARC reports:
- **Supported formats**: .xml, .gz, .zip (NEW!)
- **ZIP handling**: Automatic extraction and processing of all files
- **Progress feedback**: Real-time extraction and processing status
- **Error recovery**: Graceful handling of corrupted or invalid files

**Example workflow:**
```
1. Click "Process DMARC Report" from Tools menu
2. Select one or more report files (including .zip archives)
3. ZIP files are automatically extracted to secure directory
4. Each report is processed individually with progress display
5. Results and statistics are shown in the dialog
```

### Stock Level Management

Edit inventory with the built-in editor:
- Add new items with quantity and minimum thresholds
- Edit existing items directly in the GUI
- Delete items (confirmation required)
- Save changes to CSV file
- CSV DictWriter prevents injection attacks

### SKU Management

Manage product SKUs and materials:
- Create new SKUs with descriptions
- Link materials to products
- Edit SKU information
- Delete SKUs (confirmation required)
- Changes persist to JSON file

Troubleshooting
---------------

### Application Won't Start
**Issue**: Module not found or Python error
```
Solution: Check Python installation
python --version  # Should show 3.10+
```

### GUI Looks Blurry
**Solution**: This is a Tkinter on Windows scaling issue. Use the `.exe` instead.

### Modules Don't Run
**Solution**: Check that all helper scripts exist in their configured paths.

### Output Not Showing
**Solution**: Ensure target scripts are Python executables with proper permissions.

### Windows Centering Issue
**Solution**: Verify your monitor configuration. Fallback positioning will apply if primary monitor detection fails.

### ZIP Upload Fails
**Solution**: 
- Ensure ZIP file is valid and not corrupted
- Check file permissions
- Verify enough disk space in reports directory

Files and Structure
-------------------

```
app_gui.py                     - Main application (v1.20)
Toolkit V1.11.exe              - Standalone executable
Toolkit V1.11.spec             - PyInstaller configuration
AmeliaRoseIcon.ico             - Application icon

requirements.txt               - Python dependencies (standard library only)
run_with_venv.bat              - Batch launcher with venv
run_with_venv.ps1              - PowerShell launcher with venv
venv/                          - Virtual environment (create with setup guide)

Documentation:
├── README.md                  - This file
├── QUICKSTART.md              - Getting started guide
├── ARCHITECTURE.md            - System design and architecture
├── DOCUMENTATION.md           - Comprehensive feature documentation
├── VENV_SETUP_GUIDE.md        - Virtual environment setup
├── PROJECT_ANALYSIS_AND_UPDATES.md - Detailed analysis report
├── MENU_DESIGN_GUIDE.md       - UI design documentation
├── SECURITY_PERFORMANCE_AUDIT.md - Security review
└── PROJECT_COMPLETION_SUMMARY.md - Project status

Modules and Tools:
├── order_intake/              - Order processing module
├── pricing/                   - Pricing calculator
├── stock/                     - Stock level checker
├── customers/                 - Customer management
├── maintenance/               - Maintenance scheduling
└── security/dmarc/            - DMARC report processing
```

Development & Deployment
------------------------

### Using Virtual Environment (Recommended)

1. **Create virtual environment**:
   ```powershell
   python -m venv venv
   ```

2. **Activate it**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies** (none required, but good practice):
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run application**:
   ```powershell
   python app_gui.py
   ```

5. **Deactivate when done**:
   ```powershell
   deactivate
   ```

### Building the Executable

Update the executable with latest code:
```powershell
# Using existing spec file
pyinstaller "Toolkit V1.11.spec"

# Or fresh build
pyinstaller --onefile --windowed --name "Toolkit V1.11" --icon=AmeliaRoseIcon.ico app_gui.py
```

### Project Dependencies

**External Dependencies**: None!

This project uses only Python's standard library:
- tkinter (GUI)
- csv, json (data management)
- zipfile (archive handling)
- subprocess, threading (execution)
- logging, pathlib (utilities)

All included with Python 3.10+

Security & Performance
----------------------

### Security Features
- ✅ Path traversal prevention: `validate_file_path()`
- ✅ CSV injection protection: `sanitize_input()`
- ✅ Input validation on all user data
- ✅ Subprocess timeout: 300 seconds
- ✅ Thread-safe operation with queues
- ✅ Comprehensive error logging

### Performance Optimizations
- ✅ Thread-based output capture (non-blocking)
- ✅ Queue-based message passing (efficient)
- ✅ Lazy module loading
- ✅ Persistent theme/geometry caching
- ✅ Minimal memory footprint (no external dependencies)

See [SECURITY_PERFORMANCE_AUDIT.md](SECURITY_PERFORMANCE_AUDIT.md) for detailed review.

Getting Help
------------

1. **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
2. **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Features**: See [DOCUMENTATION.md](DOCUMENTATION.md)
4. **Keyboard Help**: Press Ctrl+K or use Help → Keyboard Shortcuts
5. **About**: Help → About for version and company info

License & Notes
---------------

**License**: See [LICENSE](LICENSE) file

**Status**: Production Ready (v1.20)

**Support**: For issues or feature requests, refer to project documentation.

**Version History**:
- v1.20 (Jan 31, 2026) - Window centering, ZIP support, venv setup
- v1.11 (Modern UI Edition) - Complete redesign with dark mode
- v1.0 (Legacy) - Original version

---

**Last Updated**: January 31, 2026  
**Maintained by**: AmeliaRoseCo  
**Repository**: AmeliaRoseCo Toolkit
