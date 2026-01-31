import os
import json
import time
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Folder paths
BASE = os.path.dirname(os.path.abspath(__file__))
ORDERS_INBOX = os.path.join(BASE, "Orders_Inbox")
TO_CUT = os.path.join(BASE, "To_Cut")
PROCESSED = os.path.join(BASE, "Processed_Orders")

# Make sure folders exist
os.makedirs(ORDERS_INBOX, exist_ok=True)
os.makedirs(TO_CUT, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

# Theme colors
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

# Patterns to extract order details
patterns = {
    "customer": r"Customer[:\- ]+(.*)",
    "product": r"Product[:\- ]+(.*)",
    "material": r"Material[:\- ]+(.*)",
    "due_date": r"Due[:\- ]+(.*)",
    "notes": r"Notes[:\- ]+(.*)"
}

def extract_details(text):
    details = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        details[key] = match.group(1).strip() if match else "NOT PROVIDED"
    return details

def create_job_card(details, filename):
    base_name = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    job_id = f"{base_name}_{timestamp}"

    job_data = {
        "job_id": job_id,
        "customer": details["customer"],
        "product": details["product"],
        "material": details["material"],
        "due_date": details["due_date"],
        "notes": details["notes"],
        "created": timestamp
    }

    # Save JSON
    json_path = os.path.join(TO_CUT, f"{job_id}.json")
    with open(json_path, "w") as f:
        json.dump(job_data, f, indent=4)

    # Save TXT summary
    txt_path = os.path.join(TO_CUT, f"{job_id}.txt")
    with open(txt_path, "w") as f:
        f.write(
            f"Job ID: {job_id}\n"
            f"Customer: {details['customer']}\n"
            f"Product: {details['product']}\n"
            f"Material: {details['material']}\n"
            f"Due Date: {details['due_date']}\n"
            f"Notes: {details['notes']}\n"
        )

    return json_path, txt_path

def process_single_order(filepath):
    """Process a single order file."""
    try:
        filename = os.path.basename(filepath)
        with open(filepath, "r", errors="ignore") as f:
            text = f.read()
        
        details = extract_details(text)
        json_path, txt_path = create_job_card(details, filename)
        
        # Move original file to processed folder
        os.rename(filepath, os.path.join(PROCESSED, filename))
        
        return {"success": True, "job_id": json_path, "details": details}
    except Exception as e:
        logger.error(f"Error processing order: {e}")
        return {"success": False, "error": str(e)}


class OrderIntakeGUI(tk.Tk):
    """GUI for order intake and prep management."""
    
    def __init__(self):
        """Initialize Order Intake GUI."""
        super().__init__()
        
        self.title("📦 Order Intake & Prep")
        self.geometry("750x700")
        self.resizable(True, True)
        
        # Try to set icon
        try:
            for icon in [
                os.path.join(os.path.dirname(BASE), "arc-tk-pastel.ico"),
                os.path.join(os.path.dirname(BASE), "AmeliaRoseIcon.ico"),
            ]:
                if os.path.exists(icon):
                    if os.name == 'nt':
                        self.iconbitmap(icon)
                    break
        except:
            pass
        
        self.dark_mode = True
        self.palette = COLORS["dark"]
        self.config(bg=self.palette["bg"])
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.watching = False
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create UI widgets."""
        # Header
        header = tk.Frame(self, bg=self.palette["accent"], height=50)
        header.pack(fill="x")
        header_label = tk.Label(header, text="📦 Order Intake & Prep Management",
                                bg=self.palette["accent"], fg="#FFFFFF",
                                font=("Segoe UI", 14, "bold"), pady=10)
        header_label.pack()
        
        # Main frame
        main = ttk.Frame(self, padding=15)
        main.pack(fill="both", expand=True)
        
        # ===== ORDER DETAILS SECTION =====
        details_frame = ttk.LabelFrame(main, text="📋 Enter Order Details", padding=10)
        details_frame.pack(fill="x", pady=10)
        
        # Customer
        ttk.Label(details_frame, text="Customer:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.customer_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.customer_var, width=40).grid(row=0, column=1, sticky="ew", padx=10, pady=8)
        
        # Product
        ttk.Label(details_frame, text="Product:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.product_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.product_var, width=40).grid(row=1, column=1, sticky="ew", padx=10, pady=8)
        
        # Material
        ttk.Label(details_frame, text="Material:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        self.material_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.material_var, width=40).grid(row=2, column=1, sticky="ew", padx=10, pady=8)
        
        # Due Date
        ttk.Label(details_frame, text="Due Date:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        self.due_date_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.due_date_var, width=40).grid(row=3, column=1, sticky="ew", padx=10, pady=8)
        
        # Notes
        ttk.Label(details_frame, text="Notes:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=8)
        self.notes_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.notes_var, width=40).grid(row=4, column=1, sticky="ew", padx=10, pady=8)
        
        details_frame.columnconfigure(1, weight=1)
        
        # ===== OUTPUT SECTION =====
        output_frame = ttk.LabelFrame(main, text="📄 Processing Log", padding=10)
        output_frame.pack(fill="both", expand=True, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=12, width=60, wrap="word",
                                                     bg=self.palette.get("input_bg", self.palette["bg"]),
                                                     fg=self.palette["fg"],
                                                     font=("Courier New", 9))
        self.output_text.pack(fill="both", expand=True)
        self.output_text.insert("1.0", "Ready to process orders. Select an order file or watch inbox.\n")
        self.output_text.config(state="disabled")
        
        # ===== BUTTONS =====
        button_frame = tk.Frame(self, bg=self.palette["bg"])
        button_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Button(button_frame, text="📁 Select File", command=self._select_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="✏️ Create Job", command=self._create_job).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📂 Open Inbox", command=self._open_inbox).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📂 View Jobs", command=self._open_to_cut).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Exit", command=self.quit).pack(side="right", padx=5)
    
    def _log_message(self, message: str, msg_type: str = "info") -> None:
        """Add message to output log."""
        self.output_text.config(state="normal")
        
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "error": "✗",
            "process": "⚙️"
        }
        icon = icons.get(msg_type, "•")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {icon} {message}\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        self.update()
    
    def _select_file(self) -> None:
        """Select an order file to process."""
        filepath = filedialog.askopenfilename(
            title="Select Order File",
            filetypes=[("Text files", "*.txt"), ("Email files", "*.eml"), ("All files", "*.*")],
            initialdir=ORDERS_INBOX
        )
        
        if filepath:
            result = process_single_order(filepath)
            if result["success"]:
                self._log_message(f"Processed: {os.path.basename(filepath)}", "success")
                self._log_message(f"Job ID: {os.path.basename(result['job_id'])}", "info")
            else:
                self._log_message(f"Error: {result['error']}", "error")
    
    def _create_job(self) -> None:
        """Create a job card manually."""
        try:
            details = {
                "customer": self.customer_var.get() or "NOT PROVIDED",
                "product": self.product_var.get() or "NOT PROVIDED",
                "material": self.material_var.get() or "NOT PROVIDED",
                "due_date": self.due_date_var.get() or "NOT PROVIDED",
                "notes": self.notes_var.get() or "NOT PROVIDED"
            }
            
            if not any([self.customer_var.get(), self.product_var.get()]):
                messagebox.showwarning("Warning", "Please enter at least Customer and Product")
                return
            
            json_path, txt_path = create_job_card(details, "manual_order")
            
            self._log_message(f"Job created: {os.path.basename(json_path)}", "success")
            self._log_message(f"Customer: {details['customer']}, Product: {details['product']}", "info")
            
            # Clear form
            self.customer_var.set("")
            self.product_var.set("")
            self.material_var.set("")
            self.due_date_var.set("")
            self.notes_var.set("")
            
        except Exception as e:
            self._log_message(f"Error creating job: {e}", "error")
    
    def _open_inbox(self) -> None:
        """Open Orders_Inbox folder."""
        if os.path.exists(ORDERS_INBOX):
            os.startfile(ORDERS_INBOX)
        else:
            messagebox.showerror("Error", "Inbox folder not found")
    
    def _open_to_cut(self) -> None:
        """Open To_Cut folder."""
        if os.path.exists(TO_CUT):
            os.startfile(TO_CUT)
        else:
            messagebox.showerror("Error", "To_Cut folder not found")


if __name__ == "__main__":
    try:
        app = OrderIntakeGUI()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application startup failed: {e}", exc_info=True)
        raise

    