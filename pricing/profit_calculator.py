"""
Profit Calculator Module
========================

Calculates profit margins and revenue projections for AmeliaRoseCo products.
Supports cost-to-price calculations with margin analysis.

Features:
- Calculate profit margin percentage
- Determine price from desired margin
- Analyze multiple items
- Export profit report
- Professional Tkinter GUI with dark mode support
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get base directory for data files
if getattr(sys, 'frozen', False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRICING_LOG = os.path.join(BASE, "pricing", "pricing_log.csv")
os.makedirs(os.path.dirname(PRICING_LOG), exist_ok=True)

# Theme colors (must match app_gui.py)
COLORS = {
    "light": {
        "bg": "#F5F5F5",
        "fg": "#1A1A1A",
        "accent": "#0078D4",
        "button_bg": "#FFFFFF",
        "button_fg": "#000000",
    },
    "dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",
        "accent": "#0E639C",
        "button_bg": "#2D2D30",
        "button_fg": "#FFFFFF",
        "input_bg": "#252526",
    }
}


class ProfitCalculator(tk.Tk):
    """Professional profit calculator with dark mode support."""
    
    def __init__(self):
        """Initialize profit calculator GUI."""
        super().__init__()
        
        self.title("💰 Profit Calculator")
        self.geometry("700x650")
        self.resizable(True, True)
        
        # Try to set icon from parent directory
        try:
            icon_candidates = [
                os.path.join(BASE, "arc-tk-pastel.ico"),
                os.path.join(BASE, "AmeliaRoseIcon.ico"),
            ]
            for icon in icon_candidates:
                if os.path.exists(icon):
                    if os.name == 'nt':
                        self.iconbitmap(icon)
                    break
        except:
            pass
        
        # Setup styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.dark_mode = True
        self.palette = COLORS["dark"]
        self.config(bg=self.palette["bg"])
        
        # Build UI
        self._create_widgets()
        self._apply_theme()
    
    def _create_widgets(self) -> None:
        """Create UI widgets."""
        # Header
        header = tk.Frame(self, bg=self.palette["accent"], height=50)
        header.pack(fill="x")
        header_label = tk.Label(header, text="💰 Profit Calculator",
                                bg=self.palette["accent"], fg="#FFFFFF",
                                font=("Segoe UI", 14, "bold"), pady=10)
        header_label.pack()
        
        # Main frame
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # ===== MODE SELECTION =====
        mode_frame = ttk.LabelFrame(main_frame, text="Calculation Mode", padding=10)
        mode_frame.pack(fill="x", pady=10)
        
        self.mode_var = tk.StringVar(value="margin")
        ttk.Radiobutton(mode_frame, text="📊 Calculate Margin %",
                        variable=self.mode_var, value="margin",
                        command=self._update_display).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="💵 Calculate Price",
                        variable=self.mode_var, value="price",
                        command=self._update_display).pack(side="left", padx=10)
        ttk.Radiobutton(mode_frame, text="📈 Batch Calculator",
                        variable=self.mode_var, value="batch",
                        command=self._update_display).pack(side="left", padx=10)
        
        # ===== INPUT FRAME =====
        self.input_frame = ttk.LabelFrame(main_frame, text="Enter Details", padding=10)
        self.input_frame.pack(fill="x", pady=10)
        
        # Cost input
        ttk.Label(self.input_frame, text="Cost ($):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.cost_var = tk.StringVar()
        self.cost_entry = ttk.Entry(self.input_frame, textvariable=self.cost_var, width=20)
        self.cost_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=8)
        
        # Price input (for margin mode)
        ttk.Label(self.input_frame, text="Price ($):", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(self.input_frame, textvariable=self.price_var, width=20)
        self.price_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=8)
        
        # Desired margin (for price mode)
        ttk.Label(self.input_frame, text="Desired Margin (%):", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.margin_var = tk.StringVar(value="30")
        self.margin_entry = ttk.Entry(self.input_frame, textvariable=self.margin_var, width=20)
        self.margin_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=8)
        
        # Description (for logging)
        ttk.Label(self.input_frame, text="Item Description:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(self.input_frame, textvariable=self.desc_var, width=20)
        self.desc_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=8)
        
        self.input_frame.columnconfigure(1, weight=1)
        
        # ===== RESULTS =====
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, width=50, wrap="word",
                                                      bg=self.palette.get("input_bg", self.palette["bg"]),
                                                      fg=self.palette["fg"],
                                                      font=("Courier New", 10))
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert("1.0", "Results will appear here...\n\n(Enter cost and price/margin, then click Calculate)")
        self.results_text.config(state="disabled")
        
        # ===== BUTTONS =====
        button_frame = tk.Frame(self, bg=self.palette["bg"])
        button_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Button(button_frame, text="📊 Calculate", command=self._calculate).pack(side="left", padx=5)
        ttk.Button(button_frame, text="💾 Save Result", command=self._save_result).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self._clear_inputs).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exit", command=self.quit).pack(side="right", padx=5)
    
    def _update_display(self) -> None:
        """Update display based on selected mode."""
        mode = self.mode_var.get()
        # Dynamic label updates could go here
        pass
    
    def _calculate(self) -> None:
        """Calculate profit based on selected mode."""
        try:
            cost = float(self.cost_var.get())
            mode = self.mode_var.get()
            
            if cost <= 0:
                messagebox.showerror("Error", "Cost must be greater than 0")
                return
            
            results = ""
            
            if mode == "margin":
                # Calculate margin from cost and price
                price = float(self.price_var.get())
                if price <= 0:
                    messagebox.showerror("Error", "Price must be greater than 0")
                    return
                
                profit = price - cost
                margin_pct = (profit / price) * 100
                
                results = f"""
╔════════════════════════════════════════╗
║         PROFIT MARGIN ANALYSIS         ║
╚════════════════════════════════════════╝

Cost (COGS):              ${cost:.2f}
Sale Price:              ${price:.2f}
─────────────────────────────────────
Profit:                  ${profit:.2f}
Margin %:                {margin_pct:.1f}%

Break-even price:        ${cost:.2f}
Min profit (10%):        ${cost * 1.10:.2f}
Recommended (30%):       ${cost * 1.30:.2f}
Premium (50%+):          ${cost * 1.50:.2f}
"""
                
            elif mode == "price":
                # Calculate price from cost and desired margin
                margin = float(self.margin_var.get())
                if margin <= 0 or margin >= 100:
                    messagebox.showerror("Error", "Margin must be between 1-99%")
                    return
                
                # Price = Cost / (1 - Margin%)
                required_price = cost / (1 - margin/100)
                profit = required_price - cost
                
                results = f"""
╔════════════════════════════════════════╗
║         PRICING RECOMMENDATION         ║
╚════════════════════════════════════════╝

Cost (COGS):              ${cost:.2f}
Target Margin:           {margin:.1f}%
─────────────────────────────────────
Required Price:          ${required_price:.2f}
Expected Profit:         ${profit:.2f}

Price Breakdown:
  Cost component:        {(cost/required_price)*100:.1f}%
  Profit component:      {margin:.1f}%
  
Alternative prices:
  15% margin:            ${cost / (1 - 0.15):.2f}
  25% margin:            ${cost / (1 - 0.25):.2f}
  40% margin:            ${cost / (1 - 0.40):.2f}
"""
            
            # Display results
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", results)
            self.results_text.config(state="disabled")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {e}")
            logger.error(f"Calculation error: {e}")
    
    def _save_result(self) -> None:
        """Save calculation result to pricing log."""
        try:
            cost = float(self.cost_var.get())
            price = float(self.price_var.get()) if self.price_var.get() else None
            desc = self.desc_var.get() or "Manual Calculation"
            
            if not price:
                messagebox.showwarning("Warning", "Enter both cost and price to save")
                return
            
            margin = ((price - cost) / price) * 100
            
            # Log to CSV
            file_exists = os.path.exists(PRICING_LOG)
            with open(PRICING_LOG, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "Description", "Cost", "Price", "Margin%", "Profit"])
                
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    desc,
                    f"${cost:.2f}",
                    f"${price:.2f}",
                    f"{margin:.1f}%",
                    f"${price - cost:.2f}"
                ])
            
            messagebox.showinfo("Success", "Calculation saved to pricing log!")
            logger.info(f"Saved calculation: {desc} - Cost: ${cost}, Price: ${price}, Margin: {margin:.1f}%")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
            logger.error(f"Save error: {e}")
    
    def _clear_inputs(self) -> None:
        """Clear all input fields."""
        self.cost_var.set("")
        self.price_var.set("")
        self.margin_var.set("30")
        self.desc_var.set("")
        self.cost_entry.focus()
    
    def _apply_theme(self) -> None:
        """Apply color theme to all widgets."""
        self.config(bg=self.palette["bg"])


if __name__ == "__main__":
    try:
        app = ProfitCalculator()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        raise
