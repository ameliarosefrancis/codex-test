# Next Steps - Remaining Phase 2 Tasks

**Current Status:** 8 of 13 tasks completed (61%)  
**Last Updated:** January 31, 2026

---

## 📋 Remaining High-Priority Tasks

### Task 1: Professional Print Dialog (COMPLEX)
**Priority:** HIGH  
**Complexity:** ⭐⭐⭐⭐⭐ (Most complex remaining task)

**What's Needed:**
Implement a Microsoft Word-style print dialog for the shopping list with:
- Printer selection (network & local)
- Page range options (all / from-to / selection)
- Number of copies input
- Orientation (Portrait/Landscape)
- Paper size selection (A4, Letter, etc.)
- Print preview
- Advanced options

**Current Code Location:**
- Function: `_print_shopping_list()` (around line 1560)
- File: `app_gui.py`

**Research Needed:**
- Windows API integration (`win32print` module)
- Or: Use `tkinter.print` module (limited but built-in)
- Alternative: PyQt5/PySide2 (adds dependency)

**Estimated Effort:** 4-6 hours

**Related User Request:**
> "Print shopping list... make it gui user friendly like a Microsoft word print menu where you can alter print options"

---

### Task 2: Fix Stock Checker Nested Windows (MEDIUM)
**Priority:** MEDIUM  
**Complexity:** ⭐⭐⭐ (Module-specific issue)

**What's Needed:**
Fix the "Russian doll" nested window issue in stock_checker.py where:
- Opening Stock Checker module opens another instance of app_gui window
- Should instead open only the stock checker interface

**Investigation Required:**
1. Review `stock/stock_checker.py` source code
2. Check if it's importing/launching app_gui incorrectly
3. Isolate stock checker UI into standalone module
4. Prevent main app window instantiation

**File Location:**
- `stock/stock_checker.py`

**Related User Request:**
> "Look into the stock level checker module... opens another app_gui windows like a Russian doll"

**Estimated Effort:** 2-3 hours

---

### Task 3: Module GUI Improvements (MEDIUM-LOW)
**Priority:** MEDIUM  
**Complexity:** ⭐⭐⭐⭐ (Multiple modules)

**What's Needed:**
Review and enhance 4 module GUIs to follow best practices and dark mode:

#### 3a. Profit Calculator (`pricing/profit_calculator.py`)
- [ ] Implement dark mode compliance
- [ ] Add proper button layout (OK/Cancel, not Save/Close)
- [ ] Improve form validation
- [ ] Add error messages for invalid inputs
- [ ] Follow modern UI standards

#### 3b. Order Intake & Prep (`order_intake/watcher.py`)
- [ ] Review UI design
- [ ] Improve dark mode support
- [ ] Add status indicators
- [ ] Ensure keyboard shortcuts work
- [ ] Clean up button layout

#### 3c. Customer Follow-Up (`customers/follow_up.py`)
- [ ] Dark mode compliance
- [ ] Professional button styling
- [ ] Template dropdown usability
- [ ] Add confirmation dialogs for send
- [ ] Real-time validation

#### 3d. Maintenance Reminders (`maintenance/reminders.py`)
- [ ] Dark mode styling
- [ ] Calendar integration (if applicable)
- [ ] Notification preferences
- [ ] Database/CSV UI improvements

**General Requirements (All Modules):**
- Follow dark mode palette from `COLORS` dict
- Use `App.set_window_icon()` for window icons
- Use `center_window_on_monitor()` for window placement
- Proper button ordering (OK on right, Cancel on left)
- Consistent font: "Segoe UI" 10pt for body, 12pt for headers

**File Locations:**
```
pricing/profit_calculator.py
order_intake/watcher.py
customers/follow_up.py
maintenance/reminders.py
```

**Related User Request:**
> "Look into creating a good easy to use gui... for profit calculator, order intake and prep... make sure they all follow best practices"

**Estimated Effort:** 6-8 hours (1.5-2 hours per module)

---

## 🔧 Implementation Strategy

### For Print Dialog:
```python
# Option A: win32print module (Windows-specific)
import win32print
import win32api

# Option B: tkinter built-in (simpler, limited)
from tkinter import filedialog
import tkinter.print

# Option C: Custom dialog (most control)
class PrintDialog(tk.Toplevel):
    def __init__(self, parent, document_data):
        # Build custom print UI
        pass
```

### For Stock Checker:
1. Audit `stock_checker.py` imports
2. Check for `if __name__ == '__main__': app = App()`
3. Replace with module-only interface
4. Test through main app only

### For Module GUIs:
1. Copy dark mode template from `app_gui.py`
2. Apply palette colors systematically
3. Add icon setting: `App.set_window_icon(self.root)` at startup
4. Update window geometry calculations
5. Test in both light and dark modes

---

## 🎯 Testing Checklist for Next Session

### Print Dialog Tests:
- [ ] Dialog opens and displays correctly
- [ ] Printer list populates
- [ ] Options update the preview
- [ ] Print button sends to correct printer
- [ ] Cancel button closes without printing
- [ ] Works in both light and dark modes
- [ ] Handles edge cases (no printers, long names, special chars)

### Stock Checker Tests:
- [ ] Launches from app_gui without nested window
- [ ] Shows module UI only
- [ ] Returns focus correctly
- [ ] No orphaned windows on close
- [ ] Error handling works

### Module GUI Tests:
- [ ] Each module opens from main app without errors
- [ ] Dark mode applied throughout
- [ ] Window icon displays
- [ ] Buttons positioned correctly
- [ ] Keyboard shortcuts work
- [ ] Form validation functions
- [ ] Saves/commits work as expected

---

## 📊 Effort Estimates

| Task | Hours | Difficulty | Session |
|------|-------|-----------|---------|
| Print Dialog | 4-6 | ⭐⭐⭐⭐⭐ | 1 session |
| Stock Checker Fix | 2-3 | ⭐⭐⭐ | 1 session |
| Module GUIs | 6-8 | ⭐⭐⭐⭐ | 2 sessions |
| Final Testing | 2-3 | ⭐⭐ | 1 session |
| **Total** | **14-20** | | **4-5 sessions** |

---

## 📝 Recommended Completion Order

### Session 1: Professional Print Dialog
- Highest complexity, most impactful
- Implement and test thoroughly
- Deploy new executable

### Session 2: Stock Checker Module
- Medium complexity, quick win
- Fix nested window issue
- Integrate with print dialog if needed
- Rebuild and test

### Session 3: Module GUI Improvements (Profit Calculator, Order Intake)
- Split into two modules for faster iteration
- Apply dark mode and best practices
- Test both modules together

### Session 4: Module GUI Improvements (Customer Follow-Up, Maintenance)
- Complete remaining two modules
- Final comprehensive testing
- Prepare for production release

---

## 💡 Best Practices Reference

### Dark Mode Palette Usage:
```python
from app_gui import COLORS

palette = COLORS["dark"]  # or ["light"]

# Apply colors
widget.config(bg=palette["bg"], fg=palette["fg"])
button.config(bg=palette["button_bg"], fg=palette["button_fg"])
```

### Icon Application:
```python
# For Toplevel windows
from app_gui import App
window = tk.Toplevel(parent)
App.set_window_icon(window)
```

### Window Centering:
```python
from app_gui import center_window_on_monitor
center_window_on_monitor(window, width=500, height=400)
```

### Standard Button Layout:
```python
# Frame for buttons
button_frame = ttk.Frame(dialog)
button_frame.pack(side="bottom", fill="x", padx=5, pady=5)

# Buttons in correct order: OK/Save on right, Cancel on left
ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
ttk.Button(button_frame, text="OK", command=save_func).pack(side="right", padx=5)
```

---

## 📞 Quick Reference

**Key Functions to Use:**
- `App.set_window_icon(window)` - Add icon to any Toplevel
- `center_window_on_monitor(window, w, h)` - Center on selected monitor
- `save_settings(settings)` - Persist user preferences
- `load_settings()` - Load saved preferences
- `COLORS["dark"]` or `COLORS["light"]` - Get theme palette

**Files to Reference:**
- `app_gui.py` - Main application (best practices examples)
- `docs/MENU_DESIGN_GUIDE.md` - UI design guidelines
- `docs/ARCHITECTURE.md` - System architecture

---

**Next Session Focus:** Professional Print Dialog Implementation  
**Estimated Session Duration:** 4-6 hours  
**Target Completion:** 2 more sessions to 100%
