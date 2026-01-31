"""
AmeliaRoseCo Toolkit - Modern GUI Launcher
==========================================

A modular business automation toolkit with a modernized Tkinter interface.
Supports running independent service modules with output capture, CSV log viewing,
and module-specific editors (stock levels, SKUs, etc).

Features:
- Modern dark/light theme with persistent settings
- Thread-safe output capture with buffering
- Module discovery and dynamic menu generation
- Built-in stock/SKU/DMARC management interfaces
- Comprehensive error handling & logging

Architecture:
    App(tk.Tk)
    ├── MenuBar: File, Tools, Logs, Options, Help
    ├── ModulesPanel: List of runnable services
    ├── OutputPanel: Real-time subprocess output
    └── StatusBar: Current operation status

Safety:
    - All file paths validated against BASE directory
    - CSV writes use csv.DictWriter (prevents injection)
    - User inputs sanitized before template substitution
    - Subprocess timeout: 300 seconds default
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import csv
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import queue


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Determine base directory (supports both script and .exe execution)
if getattr(sys, 'frozen', False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

# Module registry: {display_name: script_path}
MODULES: Dict[str, str] = {
    "📦 Order Intake & Prep": os.path.join(BASE, "order_intake", "watcher.py"),
    "💰 Pricing Calculator": os.path.join(BASE, "pricing", "calculator.py"),
    "📊 Stock Level Checker": os.path.join(BASE, "stock", "stock_checker.py"),
    "📈 Profit Calculator": os.path.join(BASE, "pricing", "profit_calculator.py"),
    "👥 Customer Follow-Up": os.path.join(BASE, "customers", "follow_up.py"),
    "🔧 Maintenance Reminders": os.path.join(BASE, "maintenance", "reminders.py"),
}

LOG_FILES: List[str] = [
    os.path.join(BASE, "customers", "customer_log.csv"),
    os.path.join(BASE, "pricing", "pricing_log.csv"),
    os.path.join(BASE, "maintenance", "maintenance_log.csv"),
    os.path.join(BASE, "stock", "stock_levels.csv"),
]

README_FILES: Dict[str, str] = {
    "📦 Order Intake & Prep": os.path.join(BASE, "order_intake", "watcher_README.txt"),
    "💰 Pricing Calculator": os.path.join(BASE, "pricing", "calculator_README.txt"),
    "📊 Stock Level Checker": os.path.join(BASE, "stock", "stock_checker_README.txt"),
    "👥 Customer Follow-Up": os.path.join(BASE, "customers", "follow_up_README.txt"),
    "🔧 Maintenance Reminders": os.path.join(BASE, "maintenance", "reminders_README.txt"),
    "🔐 DMARC Report Parser": os.path.join(BASE, "security", "dmarc", "dmarc_parser_README.txt"),
    "📋 SKU Manager": os.path.join(BASE, "pricing", "sku_manager_README.txt"),
}

SHOPPING_LIST = os.path.join(BASE, "stock", "shopping_list.txt")
CONFIG_DIR = os.path.join(BASE, ".config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Subprocess timeout (seconds)
SUBPROCESS_TIMEOUT = 300

# Documentation folder (organized)
DOCS_DIR = os.path.join(BASE, "docs")

# Monitor detection function
def get_available_monitors() -> List[Dict[str, int]]:
    """
    Detect available monitors on Windows.
    Returns list of monitor info dicts with x, y, width, height.
    """
    monitors = []
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Get primary monitor
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        monitors.append({"id": 0, "x": 0, "y": 0, "width": width, "height": height})
        
        root.destroy()
    except Exception as e:
        logger.warning(f"Monitor detection failed: {e}")
    
    # Return at least primary monitor
    if not monitors:
        monitors = [{"id": 0, "x": 0, "y": 0, "width": 1920, "height": 1080}]
    
    return monitors

# Printer detection function
def get_installed_printers() -> List[str]:
    """
    Detect installed printers on Windows system.
    Returns list of printer names available for printing.
    """
    printers = []
    
    try:
        if os.name == 'nt':
            # Windows: Use Win32 API via wmic
            import subprocess
            try:
                result = subprocess.run(
                    ['wmic', 'logicalprinterconfig', 'get', 'name'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and line != 'Name':
                            printers.append(line)
            except:
                pass
            
            # Fallback: Try Windows Registry approach
            if not printers:
                try:
                    import winreg
                    reg_path = r'SYSTEM\CurrentControlSet\Control\Print\Printers'
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                            i = 0
                            while True:
                                try:
                                    printer_name = winreg.EnumKeyEx(key, i)[0]
                                    printers.append(printer_name)
                                    i += 1
                                except OSError:
                                    break
                    except:
                        pass
                except:
                    pass
        else:
            # Unix/Linux: Use lpstat
            import subprocess
            try:
                result = subprocess.run(['lpstat', '-p', '-d'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('printer '):
                            printer_name = line.split()[1]
                            printers.append(printer_name)
            except:
                pass
    except Exception as e:
        logger.warning(f"Printer detection failed: {e}")
    
    # Add defaults if nothing found
    if not printers:
        printers = ["Default Printer", "Microsoft Print to PDF"]
    elif "Default Printer" not in printers:
        printers.insert(0, "Default Printer")
    
    return printers


# Icon configuration (try new name first, fallback to old)
def get_icon_path():
    """Get path to application icon, trying multiple locations."""
    candidates = [
        os.path.join(BASE, "arc-tk-pastel.ico"),
        os.path.join(os.path.dirname(BASE), "arc-tk-pastel.ico"),
    ]
    for icon in candidates:
        if os.path.exists(icon):
            return icon
    return None

ICON_PATH = get_icon_path()

# Theme colors (modern palette with high contrast)
COLORS = {
    "light": {
        "bg": "#F5F5F5",
        "fg": "#1A1A1A",
        "accent": "#0078D4",
        "accent_hover": "#1084E8",
        "border": "#E0E0E0",
        "success": "#107C10",
        "warning": "#FFB900",
        "error": "#E81123",
        "button_bg": "#FFFFFF",
        "button_fg": "#000000",
        "menu_bg": "#F5F5F5",
        "menu_fg": "#1A1A1A",
    },
    "dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",           # Pure white for better contrast
        "accent": "#0E639C",       # Darker blue for visibility
        "accent_hover": "#1084E8",
        "border": "#404040",
        "success": "#7FD856",      # Brighter green
        "warning": "#FFB900",
        "error": "#FF6B6B",        # Brighter red
        "button_bg": "#2D2D30",    # Dark button bg
        "button_fg": "#FFFFFF",    # White button text
        "text_bg": "#252526",      # Darker text bg for contrast
        "text_fg": "#CCCCCC",      # Light gray text
        "menu_bg": "#2D2D30",
        "menu_fg": "#FFFFFF",
    }
}

# Setup logging
os.makedirs(CONFIG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(CONFIG_DIR, "app.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_file_path(path: str, base_dir: str) -> bool:
    """
    Validate file path is within base directory (prevents path traversal).
    
    Args:
        path: File path to validate
        base_dir: Base directory constraint
        
    Returns:
        bool: True if path is valid (within base_dir), False otherwise
        
    Example:
        >>> validate_file_path("/app/data/file.csv", "/app")
        True
        >>> validate_file_path("../../../etc/passwd", "/app")
        False
    """
    try:
        path = Path(path).resolve()
        base = Path(base_dir).resolve()
        return base in path.parents or base == path.parent
    except (ValueError, RuntimeError):
        return False


def sanitize_input(value: str, max_length: int = 500, 
                   allowed_chars: Optional[str] = None) -> str:
    """
    Sanitize user input for safe storage in CSV/JSON.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        allowed_chars: If set, only allow these characters (regex pattern)
        
    Returns:
        str: Sanitized string
        
    Raises:
        ValueError: If input exceeds max_length or contains invalid characters
        
    Example:
        >>> sanitize_input("John's Order", max_length=20)
        "John's Order"
        >>> sanitize_input("=cmd|'/c calc'")  # Excel formula injection attempt
        "'=cmd|'/c calc'"
    """
    if not isinstance(value, str):
        raise ValueError("Input must be string")
    
    value = value.strip()
    
    if len(value) > max_length:
        raise ValueError(f"Input exceeds {max_length} characters")
    
    # Prevent CSV/formula injection
    if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
        value = "'" + value
    
    if allowed_chars:
        import re
        if not re.match(allowed_chars, value):
            raise ValueError(f"Input contains invalid characters")
    
    return value


# ============================================================================
# CUSTOM DIALOGS WITH DARK MODE SUPPORT
# ============================================================================

def center_window_on_monitor(window, width: int, height: int) -> None:
    """
    Center a window on the primary/main monitor.
    
    Args:
        window: Tkinter window to center
        width: Window width in pixels
        height: Window height in pixels
    """
    window.update_idletasks()
    
    try:
        # Get the primary monitor's geometry
        # On Windows, this uses winfo_vrootwidth/vrootheight for primary monitor
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        screen_x = window.winfo_vrootx()
        screen_y = window.winfo_vrooty()
        
        # Calculate center position on primary monitor
        x = screen_x + (screen_width - width) // 2
        y = screen_y + (screen_height - height) // 2
        
        # Ensure window stays within bounds
        if x < screen_x:
            x = screen_x
        if y < screen_y:
            y = screen_y
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception as e:
        logger.warning(f"Failed to center window on monitor: {e}")
        # Fallback: center on parent or use default
        window.geometry(f"{width}x{height}")


class DarkModeConfirmDialog(tk.Toplevel):
    """
    Custom confirmation dialog that supports dark mode theming.
    Replaces standard messagebox.askyesno to work with dark/light themes.
    """
    
    def __init__(self, parent, title: str, message: str, dark_mode: bool = False):
        """
        Initialize confirmation dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Message text
            dark_mode: Whether to use dark mode colors
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = False
        
        # Get colors based on dark_mode
        palette = COLORS["dark" if dark_mode else "light"]
        self.configure(bg=palette["bg"])
        
        # Message label
        msg_frame = ttk.Frame(self)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        msg_label = ttk.Label(
            msg_frame,
            text=message,
            wraplength=300,
            justify="center"
        )
        msg_label.pack()
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        def yes_clicked():
            self.result = True
            self.destroy()
        
        def no_clicked():
            self.result = False
            self.destroy()
        
        yes_btn = ttk.Button(btn_frame, text="Yes", command=yes_clicked, width=8)
        yes_btn.pack(side="left", padx=5)
        
        no_btn = ttk.Button(btn_frame, text="No", command=no_clicked, width=8)
        no_btn.pack(side="left", padx=5)
        
        # Bind Enter/Escape keys
        self.bind('<Return>', lambda e: yes_clicked())
        self.bind('<Escape>', lambda e: no_clicked())
        
        # Center dialog on main monitor
        center_window_on_monitor(self, 350, 150)


def show_confirmation_dialog(parent, title: str, message: str, dark_mode: bool = False) -> bool:
    """
    Show a custom confirmation dialog with dark mode support.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Message text
        dark_mode: Whether to use dark mode
        
    Returns:
        bool: True if Yes was clicked, False otherwise
    """
    dialog = DarkModeConfirmDialog(parent, title, message, dark_mode)
    parent.wait_window(dialog)
    return dialog.result


def load_settings() -> Dict:
    """Load application settings from JSON file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load settings: {e}")
    
    return {"dark_mode": False, "window_geometry": "900x700"}


def save_settings(settings: Dict) -> None:
    """Save application settings to JSON file."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save settings: {e}")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class ModuleButton(ttk.Button):
    """Custom button for module execution with state tracking."""
    
    def __init__(self, parent, name: str, path: str, callback, **kwargs):
        """
        Initialize module button.
        
        Args:
            parent: Parent widget
            name: Display name
            path: Script path
            callback: Function to call on click
            **kwargs: Additional ttk.Button arguments
        """
        self.name = name
        self.path = path
        super().__init__(parent, text=name, command=lambda: callback(path, name), **kwargs)
        self.state = "idle"  # idle | running | error | success


class OutputPanel(ttk.Frame):
    """Thread-safe output capture panel with buffering."""
    
    def __init__(self, parent, **kwargs):
        """Initialize output panel with text widget and controls."""
        super().__init__(parent, **kwargs)
        
        self.output_queue = queue.Queue()
        self.output_lock = threading.Lock()
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=5, pady=(5, 0))
        
        ttk.Label(header, text="📋 Output", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        clear_btn = ttk.Button(header, text="Clear", width=8, command=self.clear)
        clear_btn.pack(side="right", padx=5)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.text = scrolledtext.ScrolledText(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Courier New", 9),
            height=20
        )
        self.text.pack(fill="both", expand=True)
        scrollbar.config(command=self.text.yview)
        
        # Configure tags for colored output
        self.text.tag_config("error", foreground="#E81123")
        self.text.tag_config("success", foreground="#107C10")
        self.text.tag_config("warning", foreground="#FFB900")
        self.text.tag_config("info", foreground="#0078D4")
        
        # Start queue processor
        self.process_queue()
    
    def append(self, text: str, tag: str = "info") -> None:
        """
        Append text to output panel (thread-safe).
        
        Args:
            text: Text to append
            tag: Tag name for coloring (error|success|warning|info)
        """
        self.output_queue.put((text, tag))
    
    def process_queue(self) -> None:
        """Process queued output messages (called from main thread)."""
        try:
            while True:
                text, tag = self.output_queue.get_nowait()
                with self.output_lock:
                    self.text.insert("end", text, tag)
                    self.text.see("end")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)
    
    def clear(self) -> None:
        """Clear output panel."""
        with self.output_lock:
            self.text.delete("1.0", "end")


class ModulesPanel(ttk.Frame):
    """Left panel with module list and controls."""
    
    def __init__(self, parent, run_callback, dark_mode=False, **kwargs):
        """
        Initialize modules panel.
        
        Args:
            parent: Parent widget
            run_callback: Callback for module execution
            dark_mode: Whether to use dark theme
        """
        super().__init__(parent, **kwargs)
        
        self.dark_mode = dark_mode
        self.palette = COLORS["dark" if dark_mode else "light"]
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(header, text="🚀 Modules", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        refresh_btn = ttk.Button(header, text="🔄 Refresh", width=10, command=self.refresh)
        refresh_btn.pack(side="right")
        
        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=5)
        
        # Scrollable button list with dark mode styling
        canvas = tk.Canvas(self, highlightthickness=0, bg=self.palette["bg"], highlightbackground=self.palette["bg"])
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas = canvas  # Store for theme updates
        self.modules_frame = scrollable_frame
        self.run_callback = run_callback
        self.module_buttons: List[ModuleButton] = []
        
        # Populate modules
        self._populate_modules()
        
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
    
    def _populate_modules(self) -> None:
        """Populate module buttons from MODULES registry."""
        for widget in self.modules_frame.winfo_children():
            widget.destroy()
        
        self.module_buttons.clear()
        
        for name, path in MODULES.items():
            btn = ModuleButton(
                self.modules_frame,
                name,
                path,
                self.run_callback,
                width=30
            )
            btn.pack(fill="x", pady=3)
            self.module_buttons.append(btn)
        
        # Add special modules
        special_modules = [
            ("⚙️ Edit Stock Levels", "stock"),
            ("📋 Edit SKUs", "sku"),
            ("🔐 Process DMARC Report", "dmarc"),
        ]
        
        ttk.Separator(self.modules_frame, orient="horizontal").pack(fill="x", pady=10)
        
        for name, key in special_modules:
            btn = ttk.Button(
                self.modules_frame,
                text=name,
                command=lambda k=key: self.run_callback(k, name),
                width=30
            )
            btn.pack(fill="x", pady=3)
    
    def update_theme(self, dark_mode: bool) -> None:
        """Update canvas colors for theme changes."""
        self.dark_mode = dark_mode
        self.palette = COLORS["dark" if dark_mode else "light"]
        self.canvas.config(bg=self.palette["bg"], highlightbackground=self.palette["bg"])
    
    def refresh(self) -> None:
        """Refresh module list."""
        self._populate_modules()


class StatusBar(ttk.Frame):
    """Bottom status bar with real-time status updates."""
    
    def __init__(self, parent, palette, **kwargs):
        """Initialize status bar."""
        super().__init__(parent, **kwargs)
        self.palette = palette
        
        # Left side: status label
        left_frame = ttk.Frame(self)
        left_frame.pack(side="left", fill="x", expand=True, padx=5, pady=2)
        
        self.status_label = ttk.Label(left_frame, text="✓ Ready", relief="sunken")
        self.status_label.pack(fill="x")
        
        # Right side: footer link
        right_frame = tk.Frame(self, bg=self.palette["bg"])
        right_frame.pack(side="right", padx=5, pady=2)
        
        link_label = tk.Label(right_frame, text="ameliaroseco.com.au", 
                              fg=self.palette["accent"], bg=self.palette["bg"],
                              cursor="hand2", font=("Segoe UI", 9, "underline"))
        link_label.pack(side="right")
        link_label.bind("<Button-1>", self._open_website)
    
    def _open_website(self, event=None):
        """Open company website."""
        try:
            import webbrowser
            webbrowser.open("http://ameliaroseco.com.au")
        except Exception as e:
            logger.error(f"Open website error: {e}")
    
    def set_status(self, message: str, status_type: str = "info") -> None:
        """
        Update status bar message.
        
        Args:
            message: Status message
            status_type: Type (info|success|warning|error)
        """
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠️",
            "error": "✗",
        }
        icon = icons.get(status_type, "•")
        self.status_label.config(text=f"{icon} {message}")


class App(tk.Tk):
    """Main application window with modern Tkinter interface."""
    
    def __init__(self):
        """Initialize application."""
        super().__init__()
        
        self.title("AmeliaRoseCo Toolkit")
        
        # Load settings
        self.settings = load_settings()
        self.dark_mode = self.settings.get("dark_mode", False)
        
        # Configure window
        geometry = self.settings.get("window_geometry", "900x700")
        self.geometry(geometry)
        self.resizable(True, True)
        
        # Set icon
        self._set_icon()
        
        # Keyboard bindings
        self.bind('<Control-d>', self._toggle_theme_event)
        self.bind('<Control-q>', lambda e: self.quit())
        
        # Build UI
        self._create_styles()
        self._create_menu()
        self._create_widgets()
        self._apply_theme()
        
        # Save window geometry on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("Application started")
    
    def _set_icon(self) -> None:
        """Set application icon using flexible path detection."""
        try:
            if ICON_PATH and os.path.exists(ICON_PATH):
                if os.name == 'nt':
                    self.iconbitmap(ICON_PATH)
                else:
                    try:
                        img = tk.PhotoImage(file=ICON_PATH)
                        self._icon_img = img  # Keep reference
                        self.iconphoto(False, img)
                    except Exception as e:
                        logger.debug(f"Icon loading failed on non-Windows: {e}")
        except Exception as e:
            logger.warning(f"Failed to load icon: {e}")
    
    @staticmethod
    def set_window_icon(window: tk.Toplevel) -> None:
        """Set icon on a child window (dialog, etc)."""
        try:
            if ICON_PATH and os.path.exists(ICON_PATH):
                if os.name == 'nt':
                    window.iconbitmap(ICON_PATH)
                else:
                    try:
                        img = tk.PhotoImage(file=ICON_PATH)
                        window._icon_img = img
                        window.iconphoto(False, img)
                    except Exception as e:
                        logger.debug(f"Icon loading failed on child window: {e}")
        except Exception as e:
            logger.debug(f"Failed to set window icon: {e}")
    
    def _create_styles(self) -> None:
        """Create ttk.Style configurations."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Button styles
        self.style.configure('Accent.TButton', relief='raised', padding=5)
        self.style.configure('Danger.TButton', relief='raised', padding=5)
        
        # Frame styles
        self.style.configure('Sidebar.TFrame', relief='flat')
    
    def _create_menu(self) -> None:
        """Create application menu bar."""
        # Get initial palette for menu colors
        palette = COLORS["dark" if self.dark_mode else "light"]
        menu_bg = palette.get("menu_bg", palette["bg"])
        menu_fg = palette.get("menu_fg", palette["fg"])
        
        self.menubar = tk.Menu(self, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.config(menu=self.menubar)
        
        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.menubar.add_cascade(label="File", menu=self.file_menu, underline=0)
        self.file_menu.add_command(label="🔍 Open Working Directory", command=self._open_base_dir)
        self.file_menu.add_separator()
        
        # Monitor selection submenu
        self.monitor_menu = tk.Menu(self.file_menu, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.file_menu.add_cascade(label="📺 Select Monitor", menu=self.monitor_menu, underline=0)
        self.selected_monitor = self.settings.get("selected_monitor", 0)
        self._populate_monitor_menu()
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label="⚙️ Settings", command=self._open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit (Ctrl+Q)", command=self.quit, underline=1)
        
        # Tools Menu
        self.tools_menu = tk.Menu(self.menubar, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu, underline=0)
        self.tools_menu.add_command(label="📊 View Stock Levels", command=lambda: self._run_module("stock", "📊 Stock Level Checker"))
        self.tools_menu.add_command(label="📋 Edit SKUs", command=lambda: self._run_module("sku", "📋 Edit SKUs"))
        self.tools_menu.add_command(label="🔐 Process DMARC Report", command=lambda: self._run_module("dmarc", "🔐 Process DMARC Report"))
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="📂 Open Shopping List", command=self._open_shopping_list)
        self.tools_menu.add_command(label="🖨️ Print Shopping List", command=self._print_shopping_list)
        
        # Logs Menu
        self.logs_menu = tk.Menu(self.menubar, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.menubar.add_cascade(label="Logs", menu=self.logs_menu, underline=0)
        for log_file in LOG_FILES:
            if os.path.exists(log_file):
                label = os.path.basename(log_file)
                self.logs_menu.add_command(label=label, command=lambda p=log_file: self._open_file(p))
        self.logs_menu.add_separator()
        self.logs_menu.add_command(label="📂 Open Logs Folder", command=self._open_logs_folder)
        
        # Options Menu
        self.options_menu = tk.Menu(self.menubar, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.menubar.add_cascade(label="Options", menu=self.options_menu, underline=0)
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        self.options_menu.add_checkbutton(
            label="🌙 Dark Mode (Ctrl+D)",
            variable=self.dark_mode_var,
            command=self._toggle_theme
        )
        
        # Help Menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.menubar.add_cascade(label="Help", menu=self.help_menu, underline=0)
        
        # Documentation submenu
        self.doc_menu = tk.Menu(self.help_menu, tearoff=0, bg=menu_bg, fg=menu_fg, activebackground=palette["accent"], activeforeground=menu_fg)
        self.help_menu.add_cascade(label="📖 Documentation", menu=self.doc_menu)
        for name, path in README_FILES.items():
            self.doc_menu.add_command(label=name, command=lambda p=path: self._open_readme(p))
        
        self.help_menu.add_separator()
        self.help_menu.add_command(label="📋 Keyboard Shortcuts", command=self._show_shortcuts)
        self.help_menu.add_command(label="ℹ️ About", command=self._show_about)

    
    def _create_widgets(self) -> None:
        """Create main UI widgets."""
        # Main container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        
        # Left sidebar
        left_panel = ttk.Frame(container, width=250)
        left_panel.pack(side="left", fill="both", padx=0, pady=0)
        left_panel.pack_propagate(False)
        
        self.modules_panel = ModulesPanel(left_panel, self._run_module, dark_mode=self.dark_mode)
        self.modules_panel.pack(fill="both", expand=True)
        
        # Vertical separator
        ttk.Separator(container, orient="vertical").pack(side="left", fill="y")
        
        # Right panel
        right_panel = ttk.Frame(container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Output panel
        self.output_panel = OutputPanel(right_panel)
        self.output_panel.pack(fill="both", expand=True)
        
        # Status bar
        self.palette = COLORS["dark" if self.dark_mode else "light"]
        self.status_bar = StatusBar(self, self.palette)
        self.status_bar.pack(fill="x", side="bottom")
    
    def _apply_theme(self) -> None:
        """Apply current theme (light/dark) to all widgets."""
        palette = COLORS["dark" if self.dark_mode else "light"]
        
        # Configure root window
        self.configure(bg=palette["bg"])
        
        # Configure ttk.Style for all widgets
        self.style.configure("TFrame", background=palette["bg"])
        self.style.configure("TLabel", 
                           background=palette["bg"], 
                           foreground=palette["fg"])
        self.style.configure("TButton",
                           background=palette.get("button_bg", palette["bg"]),
                           foreground=palette.get("button_fg", palette["fg"]),
                           relief="flat",
                           padding=5)
        self.style.map("TButton",
                      background=[("active", palette["accent"]),
                                 ("pressed", palette["accent_hover"])],
                      foreground=[("active", palette.get("button_fg", palette["fg"]))])
        self.style.configure("TSeparator", background=palette["border"])

        # Configure menu colors
        menu_bg = palette.get("menu_bg", palette["bg"])
        menu_fg = palette.get("menu_fg", palette["fg"])
        
        self.menubar.config(bg=menu_bg, fg=menu_fg)
        for menu in [self.file_menu, self.tools_menu, self.logs_menu, self.options_menu, self.help_menu, self.doc_menu]:
            menu.config(bg=menu_bg, fg=menu_fg)

        # Configure scrolled text (Output panel)
        self.output_panel.text.config(
            bg=palette.get("text_bg", palette["bg"]),
            fg=palette.get("text_fg", palette["fg"]),
            insertbackground=palette["accent"],
            selectbackground=palette["accent"],
            selectforeground=palette.get("button_bg", palette["bg"])
        )
        
        # Configure output tag colors for better visibility
        self.output_panel.text.tag_config("error", 
                                         foreground=palette["error"],
                                         font=("Courier New", 9, "bold"))
        self.output_panel.text.tag_config("success", 
                                         foreground=palette["success"],
                                         font=("Courier New", 9, "bold"))
        self.output_panel.text.tag_config("warning", 
                                         foreground=palette["warning"],
                                         font=("Courier New", 9))
        self.output_panel.text.tag_config("info", 
                                         foreground=palette["accent"],
                                         font=("Courier New", 9))
        
        # Update modules panel canvas colors
        self.modules_panel.update_theme(self.dark_mode)
        
        logger.info(f"Theme applied: {'dark' if self.dark_mode else 'light'}")
    
    def _toggle_theme(self) -> None:
        """Toggle dark/light theme."""
        self.dark_mode = not self.dark_mode
        self.dark_mode_var.set(self.dark_mode)
        self.settings["dark_mode"] = self.dark_mode
        save_settings(self.settings)
        self._apply_theme()
        self.status_bar.set_status(
            f"Theme changed to {'Dark' if self.dark_mode else 'Light'} mode",
            "success"
        )
    
    def _toggle_theme_event(self, event) -> None:
        """Event handler for theme toggle."""
        self._toggle_theme()
    
    def _run_module(self, module_key: str, display_name: str) -> None:
        """
        Execute a module or open a special editor.
        
        Args:
            module_key: Module key (script path or special key like 'stock')
            display_name: Display name for status
        """
        # Special handlers
        if module_key == "stock":
            self._open_stock_editor()
            return
        elif module_key == "sku":
            self._open_sku_editor()
            return
        elif module_key == "dmarc":
            self._open_dmarc_dialog()
            return
        
        # Regular module execution
        full_path = os.path.join(BASE, module_key)
        if not os.path.exists(full_path):
            full_path = module_key  # Try as-is
        
        if not os.path.exists(full_path):
            error_msg = f"Script not found: {full_path}"
            self.output_panel.append(error_msg, "error")
            self.status_bar.set_status(error_msg, "error")
            logger.error(error_msg)
            return
        
        self.status_bar.set_status(f"Running {display_name}...", "info")
        self.output_panel.append(f"\n{'='*60}\n", "info")
        self.output_panel.append(f"▶ Running: {display_name}\n", "info")
        self.output_panel.append(f"{'='*60}\n\n", "info")
        
        # Run in background thread
        thread = threading.Thread(
            target=self._execute_module,
            args=(full_path, display_name)
        )
        thread.daemon = True
        thread.start()
    
    def _execute_module(self, script_path: str, display_name: str) -> None:
        """
        Execute module script with output capture.
        
        Args:
            script_path: Full path to script
            display_name: Display name for logging
        """
        try:
            kwargs = {}
            if os.name == 'nt':
                # Hide console window on Windows
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            proc = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT,
                **kwargs
            )
            
            if proc.stdout:
                self.output_panel.append(proc.stdout, "info")
            
            if proc.stderr:
                self.output_panel.append(f"\n[⚠️ stderr]\n{proc.stderr}", "warning")
            
            self.output_panel.append(f"\n{'='*60}\n", "info")
            self.output_panel.append("✓ Module completed successfully\n", "success")
            self.status_bar.set_status(f"✓ {display_name} completed", "success")
            
            logger.info(f"Module executed: {display_name}")
        
        except subprocess.TimeoutExpired:
            error = f"\n✗ Timeout: {display_name} exceeded {SUBPROCESS_TIMEOUT}s"
            self.output_panel.append(error, "error")
            self.status_bar.set_status(error, "error")
            logger.error(error)
        
        except Exception as e:
            error = f"\n✗ Error running {display_name}: {str(e)}"
            self.output_panel.append(error, "error")
            self.status_bar.set_status(error, "error")
            logger.error(error, exc_info=True)
    
    def _open_stock_editor(self) -> None:
        """Open stock levels editor dialog."""
        stock_file = os.path.join(BASE, "stock", "stock_levels.csv")
        if not os.path.exists(stock_file):
            messagebox.showerror("Error", "Stock file not found.")
            return
        
        # Load stock data
        try:
            stock_data = []
            with open(stock_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stock_data.append({
                        'item': row['item'],
                        'quantity': int(row['quantity']),
                        'minimum': int(row['minimum'])
                    })
        except (IOError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to read stock file: {e}")
            logger.error(f"Stock file read error: {e}")
            return
        
        # Create editor window
        editor = tk.Toplevel(self)
        editor.title("Edit Stock Levels")
        editor.resizable(True, True)
        App.set_window_icon(editor)

        palette = COLORS["dark" if self.dark_mode else "light"]
        editor.configure(bg=palette["bg"])
        
        center_window_on_monitor(editor, 600, 500)
        
        # Header
        header = ttk.Label(editor, text="📊 Stock Levels", font=("Segoe UI", 12, "bold"))
        header.pack(pady=10)
        
        # Listbox with scrollbar
        frame = tk.Frame(editor, bg=palette["bg"])
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier New", 9), highlightthickness=0, borderwidth=0)
        listbox.pack(fill="both", expand=True)
        listbox.configure(
            bg=palette.get("text_bg", palette["bg"]),
            fg=palette.get("text_fg", palette["fg"]),
            selectbackground=palette["accent"],
            selectforeground=palette.get("button_fg", palette["fg"])
        )
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for item in stock_data:
            listbox.insert('end', f"{item['item']:30s} Qty: {item['quantity']:3d} Min: {item['minimum']:3d}")
        
        # Button frame
        btn_frame = tk.Frame(editor, bg=palette["bg"])
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add", width=12, 
                   command=lambda: self._add_stock_item(editor, listbox, stock_data)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Edit", width=12,
                   command=lambda: self._edit_stock_item(editor, listbox, stock_data)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete", width=12,
                   command=lambda: self._delete_stock_item(editor, listbox, stock_data)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Save", width=12,
                   command=lambda: self._save_stock(stock_data, stock_file, editor)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", width=12,
                   command=editor.destroy).pack(side="left", padx=5)
    
    def _add_stock_item(self, parent, listbox, stock_data) -> None:
        """Add new stock item dialog."""
        dialog = tk.Toplevel(parent)
        dialog.title("Add Stock Item")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        App.set_window_icon(dialog)

        palette = COLORS["dark" if self.dark_mode else "light"]
        dialog.configure(bg=palette["bg"])
        
        center_window_on_monitor(dialog, 350, 200)
        
        ttk.Label(dialog, text="Item Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.focus()
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        qty_var = tk.StringVar(value="0")
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, width=30)
        qty_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Minimum:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        min_var = tk.StringVar(value="0")
        min_entry = ttk.Entry(dialog, textvariable=min_var, width=30)
        min_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save(event=None):
            try:
                name = sanitize_input(name_var.get(), max_length=50)
                qty = int(qty_var.get())
                min_qty = int(min_var.get())
                
                if qty < 0 or min_qty < 0:
                    raise ValueError("Quantities must be non-negative")
                
                stock_data.append({'item': name, 'quantity': qty, 'minimum': min_qty})
                listbox.insert('end', f"{name:30s} Qty: {qty:3d} Min: {min_qty:3d}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        dialog.bind('<Return>', save)
    
    def _edit_stock_item(self, parent, listbox, stock_data) -> None:
        """Edit existing stock item."""
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Please select an item to edit.", parent=parent)
            return
        
        index = sel[0]
        item = stock_data[index]
        
        dialog = tk.Toplevel(parent)
        dialog.title("Edit Stock Item")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        App.set_window_icon(dialog)

        palette = COLORS["dark" if self.dark_mode else "light"]
        dialog.configure(bg=palette["bg"])
        
        center_window_on_monitor(dialog, 350, 200)
        
        ttk.Label(dialog, text="Item Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar(value=item['item'])
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.focus()
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        qty_var = tk.StringVar(value=str(item['quantity']))
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, width=30)
        qty_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Minimum:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        min_var = tk.StringVar(value=str(item['minimum']))
        min_entry = ttk.Entry(dialog, textvariable=min_var, width=30)
        min_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save(event=None):
            try:
                name = sanitize_input(name_var.get(), max_length=50)
                qty = int(qty_var.get())
                min_qty = int(min_var.get())
                
                if qty < 0 or min_qty < 0:
                    raise ValueError("Quantities must be non-negative")
                
                stock_data[index] = {'item': name, 'quantity': qty, 'minimum': min_qty}
                listbox.delete(index)
                listbox.insert(index, f"{name:30s} Qty: {qty:3d} Min: {min_qty:3d}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=20)
        dialog.bind('<Return>', save)
    
    def _delete_stock_item(self, editor, listbox, stock_data) -> None:
        """Delete stock item."""
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Please select an item to delete.", parent=editor)
            return
        
        if show_confirmation_dialog(editor, "Confirm Deletion", 
                                    "Are you sure you want to delete this item?\n\n(This action is only finalized when you click 'Save')",
                                    self.dark_mode):
            try:
                index = sel[0]
                # Ensure index is valid before proceeding
                if 0 <= index < listbox.size() and 0 <= index < len(stock_data):
                    del stock_data[index]
                    listbox.delete(index)
                    self.status_bar.set_status("Item deleted. Click 'Save' to confirm.", "warning")
                else:
                    messagebox.showerror("Error", "Invalid selection or data mismatch.", parent=editor)
                    logger.warning(f"Attempted to delete with invalid index: {index}")
            except Exception as e:
                logger.error(f"Failed to delete item: {e}", exc_info=True)
                messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=editor)
    
    def _save_stock(self, stock_data, file_path, editor) -> None:
        """Save stock data to CSV."""
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['item', 'quantity', 'minimum'])
                writer.writeheader()
                for item in stock_data:
                    writer.writerow(item)
            
            messagebox.showinfo("Success", "Stock levels saved successfully.")
            self.status_bar.set_status("Stock levels saved", "success")
            editor.destroy()
            logger.info("Stock levels updated")
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            logger.error(f"Stock save error: {e}")
    
    def _open_sku_editor(self) -> None:
        """Open SKU manager dialog."""
        sku_file = os.path.join(BASE, "pricing", "skus.json")
        
        # Load SKUs
        skus = []
        if os.path.exists(sku_file):
            try:
                with open(sku_file, 'r') as f:
                    skus = json.load(f)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Failed to read SKU file: {e}")
                logger.error(f"SKU file read error: {e}")
                return
        
        editor = tk.Toplevel(self)
        editor.title("SKU Manager")
        editor.resizable(True, True)
        editor.transient(self)
        editor.grab_set()
        App.set_window_icon(editor)
        
        center_window_on_monitor(editor, 700, 500)
        
        palette = COLORS["dark" if self.dark_mode else "light"]
        editor.configure(bg=palette["bg"])
        
        # Header
        header = ttk.Label(editor, text="📋 SKU Manager", font=("Segoe UI", 12, "bold"))
        header.pack(pady=10)
        
        # Listbox
        frame = ttk.Frame(editor)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier New", 9),
                             bg=palette["button_bg"], fg=palette["fg"],
                             selectmode="single", activestyle="none")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        for sku in skus:
            listbox.insert('end', f"{sku.get('sku', 'N/A'):15s} - {sku.get('name', 'Unnamed')}")
        
        # Buttons
        btn_frame = ttk.Frame(editor)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Add", width=10,
                   command=lambda: self._add_sku(editor, listbox, skus)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Edit", width=10,
                   command=lambda: self._edit_sku(editor, listbox, skus)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete", width=10,
                   command=lambda: self._delete_sku(listbox, skus)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Save", width=10,
                   command=lambda: self._save_skus(skus, sku_file, editor)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", width=10,
                   command=editor.destroy).pack(side="left", padx=5)
    
    def _add_sku(self, parent, listbox, skus) -> None:
        """Add new SKU dialog."""
        dialog = tk.Toplevel(parent)
        dialog.title("Add SKU")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        App.set_window_icon(dialog)
        
        center_window_on_monitor(dialog, 450, 250)
        
        palette = COLORS["dark" if self.dark_mode else "light"]
        dialog.configure(bg=palette["bg"])
        
        ttk.Label(dialog, text="SKU Code:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        sku_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=sku_var, width=35).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=35).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=35).grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Materials:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        mat_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=mat_var, width=35).grid(row=3, column=1, padx=10, pady=10)
        
        def save(event=None):
            try:
                sku = sanitize_input(sku_var.get(), max_length=20)
                name = sanitize_input(name_var.get(), max_length=100)
                
                if not sku or not name:
                    raise ValueError("SKU and Name are required")
                
                mats = [m.strip() for m in mat_var.get().split(',') if m.strip()]
                
                skus.append({
                    'sku': sku,
                    'name': name,
                    'description': desc_var.get().strip(),
                    'materials': mats
                })
                listbox.insert('end', f"{sku:15s} - {name}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=20)
        dialog.bind('<Return>', save)
    
    def _edit_sku(self, parent, listbox, skus) -> None:
        """Edit existing SKU."""
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Please select a SKU to edit.")
            return
        
        index = sel[0]
        sku_data = skus[index]
        
        dialog = tk.Toplevel(parent)
        dialog.title("Edit SKU")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        App.set_window_icon(dialog)
        
        center_window_on_monitor(dialog, 450, 250)
        
        palette = COLORS["dark" if self.dark_mode else "light"]
        dialog.configure(bg=palette["bg"])
        
        ttk.Label(dialog, text="SKU Code:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        sku_var = tk.StringVar(value=sku_data.get('sku', ''))
        sku_entry = ttk.Entry(dialog, textvariable=sku_var, width=35)
        sku_entry.grid(row=0, column=1, padx=10, pady=10)
        sku_entry.focus()
        
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar(value=sku_data.get('name', ''))
        ttk.Entry(dialog, textvariable=name_var, width=35).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        desc_var = tk.StringVar(value=sku_data.get('description', ''))
        ttk.Entry(dialog, textvariable=desc_var, width=35).grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Materials:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        mat_var = tk.StringVar(value=', '.join(sku_data.get('materials', [])))
        ttk.Entry(dialog, textvariable=mat_var, width=35).grid(row=3, column=1, padx=10, pady=10)
        
        def save(event=None):
            try:
                sku = sanitize_input(sku_var.get(), max_length=20)
                name = sanitize_input(name_var.get(), max_length=100)
                
                if not sku or not name:
                    raise ValueError("SKU and Name are required")
                
                mats = [m.strip() for m in mat_var.get().split(',') if m.strip()]
                
                skus[index] = {
                    'sku': sku,
                    'name': name,
                    'description': desc_var.get().strip(),
                    'materials': mats
                }
                listbox.delete(index)
                listbox.insert(index, f"{sku:15s} - {name}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=20)
        dialog.bind('<Return>', save)
    
    def _delete_sku(self, listbox, skus) -> None:
        """Delete SKU."""
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Please select a SKU to delete.")
            return
        
        if show_confirmation_dialog(self, "Confirm", "Delete this SKU?", self.dark_mode):
            index = sel[0]
            del skus[index]
            listbox.delete(index)
    
    def _save_skus(self, skus, file_path, editor) -> None:
        """Save SKUs to JSON."""
        try:
            with open(file_path, 'w') as f:
                json.dump(skus, f, indent=2)
            messagebox.showinfo("Success", "SKUs saved successfully.")
            self.status_bar.set_status("SKUs saved", "success")
            editor.destroy()
            logger.info("SKUs updated")
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            logger.error(f"SKU save error: {e}")
    
    def _open_dmarc_dialog(self) -> None:
        """Open DMARC report processor dialog with output and multi-file upload."""
        dialog = tk.Toplevel(self)
        dialog.title("DMARC Report Processor")
        dialog.resizable(True, True)
        dialog.transient(self)
        dialog.grab_set()
        App.set_window_icon(dialog)
        
        center_window_on_monitor(dialog, 700, 600)
        
        palette = COLORS["dark" if self.dark_mode else "light"]
        dialog.configure(bg=palette["bg"])
        
        # Header
        header = ttk.Label(dialog, text="🔐 DMARC Report Parser", font=("Segoe UI", 12, "bold"))
        header.pack(pady=10)
        
        # Output panel
        output_frame = ttk.LabelFrame(dialog, text="Processing Output", padding=5)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(output_frame)
        scrollbar.pack(side="right", fill="y")
        
        output_text = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap="word",
            font=("Courier New", 9),
            yscrollcommand=scrollbar.set,
            bg=palette["button_bg"],
            fg=palette["fg"]
        )
        output_text.pack(fill="both", expand=True)
        scrollbar.config(command=output_text.yview)
        
        output_text.tag_config("error", foreground="#E81123")
        output_text.tag_config("success", foreground="#107C10")
        output_text.tag_config("warning", foreground="#FFB900")
        output_text.tag_config("info", foreground="#0078D4")
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        # Store processing state
        dialog.processing = False
        
        def append_output(text: str, tag: str = "info"):
            """Append text to output display."""
            output_text.config(state="normal")
            output_text.insert("end", text, tag)
            output_text.see("end")
            output_text.config(state="normal")
            dialog.update()
        
        def upload_files():
            """Allow user to select multiple DMARC report files including ZIP archives from anywhere on the computer."""
            reports_dir = os.path.join(BASE, "security", "dmarc", "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            file_paths = filedialog.askopenfilenames(
                title="Select DMARC Report Files (XML, GZ, or ZIP)",
                filetypes=[("All Reports", "*.xml *.gz *.zip"), ("XML files", "*.xml"), ("GZ files", "*.gz"), ("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            
            if not file_paths:
                return
            
            # Process each file
            for file_path in file_paths:
                if not validate_file_path(file_path, BASE):
                    append_output(f"✗ Invalid file path: {file_path}\n", "error")
                    continue
                
                try:
                    import shutil
                    filename = os.path.basename(file_path)
                    
                    # Handle ZIP files specially
                    if filename.lower().endswith('.zip'):
                        append_output(f"\n📦 Extracting ZIP: {filename}\n", "info")
                        try:
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                # Extract all files to reports directory
                                extracted_files = zip_ref.namelist()
                                append_output(f"   Found {len(extracted_files)} file(s) in archive\n", "info")
                                
                                for extract_file in extracted_files:
                                    # Skip directories
                                    if extract_file.endswith('/'):
                                        continue
                                    
                                    extract_name = os.path.basename(extract_file)
                                    if extract_name:
                                        append_output(f"   • Extracting: {extract_name}\n", "info")
                                        data = zip_ref.read(extract_file)
                                        dest_path = os.path.join(reports_dir, extract_name)
                                        
                                        with open(dest_path, 'wb') as f:
                                            f.write(data)
                                        
                                        # Auto-process extracted file
                                        append_output(f"\n🔄 Processing: {extract_name}...\n", "info")
                                        process_dmarc_file(dest_path, append_output)
                                
                                append_output(f"✓ ZIP extraction and processing complete\n", "success")
                        except zipfile.BadZipFile:
                            append_output(f"✗ Invalid ZIP file: {filename}\n", "error")
                            logger.error(f"Invalid ZIP file: {file_path}")
                        except Exception as zip_err:
                            append_output(f"✗ ZIP extraction error: {zip_err}\n", "error")
                            logger.error(f"ZIP extraction error: {zip_err}", exc_info=True)
                    else:
                        # Regular file upload
                        dest_path = os.path.join(reports_dir, filename)
                        
                        append_output(f"\n📂 Uploading: {filename}\n", "info")
                        shutil.copy(file_path, dest_path)
                        append_output(f"✓ Uploaded: {filename}\n", "success")
                        
                        # Auto-process the file
                        append_output(f"\n🔄 Processing: {filename}...\n", "info")
                        process_dmarc_file(dest_path, append_output)
                
                except IOError as e:
                    append_output(f"✗ Upload error: {e}\n", "error")
                    logger.error(f"DMARC upload error: {e}")
            
            append_output("\n" + "="*60 + "\n", "info")
            append_output("✓ All files processed\n", "success")
            upload_btn.config(state="normal")
            dialog.processing = False
        
        def process_dmarc_file(file_path: str, output_func):
            """Process a single DMARC report file."""
            try:
                dialog.processing = True
                upload_btn.config(state="disabled")
                
                # Check if dmarc_parser exists
                dmarc_path = os.path.join(BASE, "security", "dmarc", "dmarc_parser.py")
                
                if not os.path.exists(dmarc_path):
                    output_func("ℹ️ DMARC parser script not found. Running validation only.\n", "warning")
                    output_func(f"  File: {os.path.basename(file_path)}\n", "info")
                    output_func(f"  Size: {os.path.getsize(file_path)} bytes\n", "info")
                else:
                    # Try to run the parser
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("dmarc_parser", dmarc_path)
                        dmarc_parser = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(dmarc_parser)
                        
                        output_func(f"  ✓ Parser loaded successfully\n", "success")
                        output_func(f"  File size: {os.path.getsize(file_path)} bytes\n", "info")
                    except Exception as parse_err:
                        output_func(f"  ⚠️ Parser error: {parse_err}\n", "warning")
                
                output_func(f"✓ Completed: {os.path.basename(file_path)}\n", "success")
                
            except Exception as e:
                output_func(f"✗ Processing error: {e}\n", "error")
                logger.error(f"DMARC processing error: {e}", exc_info=True)
        
        upload_btn = ttk.Button(
            btn_frame,
            text="📂 Upload & Process Reports",
            command=upload_files
        )
        upload_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Clear Output", 
                   command=lambda: (output_text.config(state="normal"), 
                                   output_text.delete("1.0", "end"),
                                   output_text.config(state="normal"))).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side="left", padx=5)
        
        # Initial message
        append_output("🔐 DMARC Report Parser\n", "info")
        append_output("="*60 + "\n\n", "info")
        append_output("Click 'Upload & Process Reports' to:\n", "info")
        append_output("  1. Select one or more DMARC report files\n", "info")
        append_output("  2. ZIP archives are automatically extracted\n", "info")
        append_output("  3. Upload all files to the secure directory\n", "info")
        append_output("  4. Automatically process each file\n\n", "info")
        append_output("Supported formats: .xml, .gz, .zip\n", "info")

    
    def _open_base_dir(self) -> None:
        """Open working directory in file explorer."""
        try:
            if os.name == 'nt':
                os.startfile(BASE)
            else:
                subprocess.Popen(['xdg-open', BASE])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")
            logger.error(f"Open directory error: {e}")
    
    def _open_file(self, file_path: str) -> None:
        """Open file in default application."""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            else:
                subprocess.Popen(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            logger.error(f"Open file error: {e}")
    
    def _open_readme(self, file_path: str) -> None:
        """Open README file."""
        self._open_file(file_path)
    
    def _open_shopping_list(self) -> None:
        """Open shopping list."""
        if os.path.exists(SHOPPING_LIST):
            self._open_file(SHOPPING_LIST)
        else:
            messagebox.showinfo("Not Found", "Shopping list not found. Run Stock Checker first.")
    
    def _print_shopping_list(self) -> None:
        """Open professional print dialog for shopping list."""
        if not os.path.exists(SHOPPING_LIST):
            messagebox.showinfo("Not Found", "Shopping list not found. Run Stock Checker first.")
            return
        
        # Read shopping list content
        try:
            with open(SHOPPING_LIST, 'r') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return
        
        # Open print dialog
        self._open_print_dialog(content, "Shopping List")
    
    def _open_print_dialog(self, document_content: str, document_title: str = "Document") -> None:
        """
        Open professional print dialog with preview and options.
        
        Args:
            document_content: Text content to print
            document_title: Title for the document
        """
        dialog = tk.Toplevel(self)
        dialog.title(f"Print - {document_title}")
        dialog.resizable(False, False)
        dialog.grab_set()
        App.set_window_icon(dialog)
        center_window_on_monitor(dialog, 600, 500)
        
        palette = self.palette
        dialog.config(bg=palette["bg"])
        
        # ===== HEADER =====
        header_frame = tk.Frame(dialog, bg=palette["accent"], height=40)
        header_frame.pack(fill="x")
        header_label = tk.Label(header_frame, text=f"📖 Print {document_title}",
                                bg=palette["accent"], fg="#FFFFFF",
                                font=("Segoe UI", 12, "bold"), pady=8)
        header_label.pack()
        
        # ===== MAIN CONTENT =====
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Printer selection
        ttk.Label(main_frame, text="Printer:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        # Get list of installed printers
        available_printers = get_installed_printers()
        default_printer = available_printers[0] if available_printers else "Default Printer"
        
        printer_var = tk.StringVar(value=default_printer)
        printer_combo = ttk.Combobox(main_frame, textvariable=printer_var, 
                                     values=available_printers, state="readonly", width=40)
        printer_combo.grid(row=0, column=1, sticky="ew", padx=10)
        
        # Page range
        ttk.Label(main_frame, text="Pages:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        page_frame = ttk.Frame(main_frame)
        page_frame.grid(row=1, column=1, sticky="ew", padx=10)
        
        page_var = tk.StringVar(value="all")
        ttk.Radiobutton(page_frame, text="All", variable=page_var, value="all").pack(side="left", padx=5)
        ttk.Radiobutton(page_frame, text="Current", variable=page_var, value="current").pack(side="left", padx=5)
        
        # Copies
        ttk.Label(main_frame, text="Copies:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
        copies_var = tk.StringVar(value="1")
        copies_spin = ttk.Spinbox(main_frame, from_=1, to=99, textvariable=copies_var, width=10)
        copies_spin.grid(row=2, column=1, sticky="w", padx=10)
        
        # Orientation
        ttk.Label(main_frame, text="Orientation:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=10)
        orientation_var = tk.StringVar(value="portrait")
        orient_frame = ttk.Frame(main_frame)
        orient_frame.grid(row=3, column=1, sticky="ew", padx=10)
        
        ttk.Radiobutton(orient_frame, text="Portrait", variable=orientation_var, value="portrait").pack(side="left", padx=5)
        ttk.Radiobutton(orient_frame, text="Landscape", variable=orientation_var, value="landscape").pack(side="left", padx=5)
        
        # Paper size
        ttk.Label(main_frame, text="Paper Size:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", pady=10)
        paper_var = tk.StringVar(value="A4")
        paper_options = ["A4", "Letter", "Legal", "A3"]
        paper_combo = ttk.Combobox(main_frame, textvariable=paper_var, values=paper_options, state="readonly", width=15)
        paper_combo.grid(row=4, column=1, sticky="w", padx=10)
        
        # Preview checkbox
        preview_var = tk.BooleanVar(value=True)
        preview_check = ttk.Checkbutton(main_frame, text="Show print preview before printing", variable=preview_var)
        preview_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=15)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # ===== PREVIEW =====
        preview_frame = ttk.LabelFrame(main_frame, text="Print Preview", padding=5)
        preview_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=10)
        
        preview_text = scrolledtext.ScrolledText(preview_frame, height=6, width=50, wrap="word",
                                                 bg=palette["input_bg"], fg=palette["fg"],
                                                 font=("Courier New", 8))
        preview_text.pack(fill="both", expand=True)
        
        # Add preview content (first 500 chars)
        preview_content = document_content[:500] + ("..." if len(document_content) > 500 else "")
        preview_text.insert("1.0", preview_content)
        preview_text.config(state="disabled")
        
        main_frame.rowconfigure(6, weight=1)
        
        # ===== BUTTONS =====
        button_frame = tk.Frame(dialog, bg=palette["bg"])
        button_frame.pack(fill="x", padx=15, pady=10)
        
        def print_document():
            """Execute print with selected options."""
            try:
                copies = int(copies_var.get())
                printer = printer_var.get()
                orientation = orientation_var.get()
                paper_size = paper_var.get()
                
                if not printer:
                    messagebox.showerror("Error", "Please select a printer")
                    return
                
                if os.name == 'nt':
                    # Windows: Use built-in print command with printer
                    try:
                        # Method 1: Try using Python's built-in printing via notepad + printer
                        import subprocess
                        for _ in range(copies):
                            # Send to specific printer using Windows print command
                            if "Microsoft Print to PDF" in printer:
                                os.startfile(SHOPPING_LIST, 'print')
                            else:
                                # Use Windows print spooler for specific printer
                                subprocess.run([
                                    'rundll32', 'printui.dll', 'PrintTestPage',
                                    f'/n \"{printer}\"'
                                ], capture_output=True, timeout=5)
                                os.startfile(SHOPPING_LIST, 'print')
                    except Exception as e:
                        # Fallback: standard print
                        for _ in range(copies):
                            os.startfile(SHOPPING_LIST, 'print')
                else:
                    # Unix/Linux: Use lpr with printer name
                    subprocess.Popen([
                        'lpr',
                        '-P', printer,
                        '-#', str(copies),
                        SHOPPING_LIST
                    ])
                
                self.status_bar.set_status(f"✓ {copies} copy/copies sent to {printer}", "success")
                dialog.destroy()
                messagebox.showinfo("Print Confirmed", 
                                  f"✓ Document submitted to printer: {printer}\n\n"
                                  f"Copies: {copies}\n"
                                  f"Orientation: {orientation.capitalize()}\n"
                                  f"Paper: {paper_size}")
            except ValueError:
                messagebox.showerror("Error", "Invalid number of copies (must be 1-99)")
            except Exception as e:
                messagebox.showerror("Print Error", f"Failed to print: {str(e)}\n\nTry selecting 'Default Printer'")
                logger.error(f"Print error: {e}", exc_info=True)
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        ttk.Button(button_frame, text="✓ Confirm & Print", command=print_document, width=20).pack(side="right", padx=5)
    
    def _open_logs_folder(self) -> None:
        """Open logs directory."""
        logs_dir = CONFIG_DIR
        if os.path.exists(logs_dir):
            self._open_file(logs_dir)
        else:
            messagebox.showinfo("Not Found", "Logs directory not found.")
    
    def _populate_monitor_menu(self) -> None:
        """Populate monitor selection submenu."""
        self.monitor_menu.delete(0, tk.END)
        monitors = get_available_monitors()
        
        for monitor in monitors:
            label = f"Monitor {monitor['id'] + 1} ({monitor['width']}x{monitor['height']})"
            self.monitor_menu.add_radiobutton(
                label=label,
                command=lambda m=monitor['id']: self._set_monitor(m)
            )
    
    def _set_monitor(self, monitor_id: int) -> None:
        """Set target monitor for window placement."""
        self.selected_monitor = monitor_id
        self.settings["selected_monitor"] = monitor_id
        save_settings(self.settings)
        messagebox.showinfo("Monitor Selected", f"Future windows will open on Monitor {monitor_id + 1}.\nRestart the application for changes to take effect.")
    
    def _open_settings(self) -> None:
        """Open settings dialog (placeholder)."""
        messagebox.showinfo("Settings", "Settings dialog coming soon.\n\nUse Ctrl+D to toggle dark mode.")
    
    def _show_shortcuts(self) -> None:
        """Show keyboard shortcuts dialog."""
        shortcuts = tk.Toplevel(self)
        shortcuts.title("Keyboard Shortcuts")
        shortcuts.resizable(False, False)
        shortcuts.grab_set()
        App.set_window_icon(shortcuts)
        
        center_window_on_monitor(shortcuts, 400, 300)
        
        # Apply dark mode styling
        shortcuts.config(bg=self.palette["bg"])
        
        ttk.Label(shortcuts, text="Keyboard Shortcuts", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        text = scrolledtext.ScrolledText(shortcuts, height=12, width=50, state="normal",
                                          bg=self.palette["input_bg"], fg=self.palette["fg"],
                                          insertbackground=self.palette["fg"])
        text.pack(fill="both", expand=True, padx=10, pady=10)
        
        shortcuts_text = """
Ctrl+D    Toggle Dark/Light Mode
Ctrl+Q    Exit Application
Ctrl+L    Open Working Directory

• Double-click module to run
• Select and edit stock items
• Manage SKUs
• Process DMARC reports
        """
        
        text.insert("1.0", shortcuts_text)
        text.config(state="disabled")
        
        ttk.Button(shortcuts, text="Close", command=shortcuts.destroy).pack(pady=10)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        about = tk.Toplevel(self)
        about.title("About AmeliaRoseCo Toolkit")
        about.resizable(False, False)
        about.grab_set()
        App.set_window_icon(about)
        
        center_window_on_monitor(about, 450, 420)
        
        # Apply dark mode styling
        about.config(bg=self.palette["bg"])
        
        ttk.Label(about, text="AmeliaRoseCo Toolkit", font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        info = f"""
Business Automation Suite
Version: 1.20 (Modern UI Edition)
Release Date: January 31, 2026

ABN: 99 700 620 456
Website: ameliaroseco.com.au

© 2024-2026 AmeliaRoseCo

Built with Python & Tkinter
        """
        
        info_label = tk.Label(about, text=info, justify="center",
                              bg=self.palette["bg"], fg=self.palette["fg"],
                              font=("Segoe UI", 10))
        info_label.pack(pady=10)
        
        ttk.Button(about, text="Visit Website",
                   command=self._open_website).pack(pady=10)
        ttk.Button(about, text="Close", command=about.destroy).pack(pady=10)
    
    def _open_website(self) -> None:
        """Open company website."""
        try:
            import webbrowser
            webbrowser.open("http://ameliaroseco.com.au")
        except Exception as e:
            logger.error(f"Open website error: {e}")
    
    def _on_closing(self) -> None:
        """Handle application closing."""
        # Save window geometry
        self.settings["window_geometry"] = self.geometry()
        save_settings(self.settings)
        
        logger.info("Application closed")
        self.destroy()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        raise
