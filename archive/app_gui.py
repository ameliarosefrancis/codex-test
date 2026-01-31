import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json

# Get the correct base directory (works for both script and exe)
if getattr(sys, 'frozen', False):
    # Running as exe
    BASE = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE = os.path.dirname(os.path.abspath(__file__))

# Define available modules
MODULES = {
    "Order Intake & Prep Bot": os.path.join(BASE, "order_intake", "watcher.py"),
    "Pricing Calculator": os.path.join(BASE, "pricing", "calculator.py"),
    "Stock Level Checker": os.path.join(BASE, "stock", "stock_checker.py"),
    "Profit Calculator": os.path.join(BASE, "pricing", "profit_calculator.py"),
    "Customer Follow-Up Bot": os.path.join(BASE, "customers", "follow_up.py"),
    "Maintenance Reminder Bot": os.path.join(BASE, "maintenance", "reminders.py"),
}

LOG_FILES = [
    os.path.join(BASE, "customers", "customer_log.csv"),
    os.path.join(BASE, "pricing", "pricing_log.csv"),
    os.path.join(BASE, "maintenance", "maintenance_log.csv"),
    os.path.join(BASE, "stock", "stock_levels.csv"),
]

README_FILES = {
    "Order Intake & Prep Bot": os.path.join(BASE, "order_intake", "watcher_README.txt"),
    "Pricing Calculator": os.path.join(BASE, "pricing", "calculator_README.txt"),
    "Stock Level Checker": os.path.join(BASE, "stock", "stock_checker_README.txt"),
    "Customer Follow-Up Bot": os.path.join(BASE, "customers", "follow_up_README.txt"),
    "Maintenance Reminder Bot": os.path.join(BASE, "maintenance", "reminders_README.txt"),
    "DMARC Report Parser": os.path.join(BASE, "security", "dmarc", "dmarc_parser_README.txt"),
    "SKU Manager": os.path.join(BASE, "pricing", "sku_manager_README.txt"),
}

SHOPPING_LIST = os.path.join(BASE, "stock", "shopping_list.txt")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # try set application icon (use .ico in project root or parent)
        try:
            icon_path = os.path.join(BASE, "AmeliaRoseIcon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(BASE), "AmeliaRoseIcon.ico")
            if os.path.exists(icon_path):
                # on Windows use iconbitmap; on other platforms try iconphoto fallback
                if os.name == 'nt':
                    self.iconbitmap(icon_path)
                else:
                    try:
                        img = tk.PhotoImage(file=icon_path)
                        # keep a reference to avoid GC
                        self._icon_img = img
                        self.iconphoto(False, img)
                    except Exception:
                        pass
        except Exception:
            pass

        self.dark_mode = False

        self.title("AmeliaRoseCo Toolkit — GUI")
        self.geometry("800x700")
        self.resizable(True, True)

        # Bind Ctrl+D for dark mode toggle
        self.bind('<Control-d>', lambda e: self.toggle_theme())

        self.create_menu()
        self.create_widgets()
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.configure(bg='#333')
            style = ttk.Style()
            style.configure('TFrame', background='#333')
            style.configure('TLabel', background='#333', foreground='white')
            style.configure('TButton', background='#555', foreground='black')
            style.configure('TCheckbutton', background='#333', foreground='white')
            # Configure Text widget
            self.output.config(bg='#333', fg='white', insertbackground='white')
            # Configure menu bar
            if hasattr(self, 'menubar'):
                self.menubar.configure(bg='#333', fg='white')
                self.file_menu.configure(bg='#333', fg='white')
                self.stock_menu.configure(bg='#333', fg='white')
                self.Logs_menu.configure(bg='#333', fg='white')
                self.options_menu.configure(bg='#333', fg='white')
                self.help_menu.configure(bg='#333', fg='white')
                self.doc_menu.configure(bg='#333', fg='white')
        else:
            self.configure(bg='white')
            style = ttk.Style()
            style.configure('TFrame', background='white')
            style.configure('TLabel', background='white', foreground='black')
            style.configure('TButton', background='lightgray', foreground='black')
            style.configure('TCheckbutton', background='white', foreground='black')
            # Configure Text widget
            self.output.config(bg='white', fg='black', insertbackground='white')
            # Configure menu bar
            if hasattr(self, 'menubar'):
                self.menubar.configure(bg='white', fg='black')
                self.file_menu.configure(bg='white', fg='black')
                self.stock_menu.configure(bg='white', fg='black')
                self.Logs_menu.configure(bg='white', fg='black')
                self.options_menu.configure(bg='white', fg='black')
                self.help_menu.configure(bg='white', fg='black')
                self.doc_menu.configure(bg='white', fg='black')

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_checkbutton(label="Exit", command=self.quit)

        # Stock menu
        self.stock_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Stock", menu=self.stock_menu)
        self.stock_menu.add_command(label="Open Shopping List", command=self.open_shopping_list)
        self.stock_menu.add_command(label="Print Shopping List", command=self.print_shopping_list)

        # Logs menu
        self.Logs_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Logs", menu=self.Logs_menu)
        for lf in LOG_FILES:
            if os.path.exists(lf):
                self.Logs_menu.add_command(label=os.path.basename(lf), command=lambda p=lf: self.open_file(p))
        

        # Options menu
        self.options_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_checkbutton(label="Dark Mode (Ctrl+D)", command=self.toggle_theme)

        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        
        # Documentation submenu
        self.doc_menu = tk.Menu(self.help_menu, tearoff=0)
        self.help_menu.add_cascade(label="Documentation", menu=self.doc_menu)
        for name, path in README_FILES.items():
            self.doc_menu.add_command(label=name, command=lambda p=path: self.open_readme(p))
        
        self.help_menu.add_command(label="About", command=self.show_about)

    def open_readme(self, path):
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.Popen(['xdg-open', path])
        else:
            messagebox.showerror('Not found', f'README not found:\n{path}')

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About")
        about_window.geometry("300x200")
        about_window.resizable(False, False)
        
        ttk.Label(about_window, text="AmeliaRoseCo", font=(None, 14, 'bold')).pack(pady=10)
        ttk.Label(about_window, text="ABN: 99700620456").pack()
        ttk.Label(about_window, text="Version: Alpha Beta V1.111").pack()
        ttk.Label(about_window, text="Release Date: 26/01/26").pack()
        
        # Website as hyperlink
        import webbrowser
        link = ttk.Label(about_window, text="ameliaroseco.com.au", foreground="blue", cursor="hand2")
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open("http://ameliaroseco.com.au"))
        
        ttk.Button(about_window, text="Close", command=about_window.destroy).pack(pady=10)

    def create_widgets(self):
        left = ttk.Frame(self, width=300)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(left, text="Available Modules", font=(None, 12, 'bold')).pack(pady=(0,5))
        self.modules_frame = ttk.Frame(left)
        self.modules_frame.pack(fill="y", expand=True)
        
        self.module_buttons = []
        self.modules = []
        
        # populate from MODULES dict
        if MODULES:
            for name, path in MODULES.items():
                self.modules.append((name, path))
        else:
            # fallback: scan top-level and folders for .py scripts
            for root, _, files in os.walk(BASE):
                for f in files:
                    if f.endswith('.py') and f not in ('app_gui.py', 'gui_launcher.py', 'gui_launcher.pyw', 'launcher.py'):
                        rel = os.path.relpath(os.path.join(root, f), BASE)
                        name = os.path.splitext(f)[0].replace('_', ' ').title()
                        self.modules.append((name, rel))
        
        # Add DMARC module
        dmarc_path = os.path.join(BASE, "security", "dmarc", "dmarc_parser.py")
        if os.path.exists(dmarc_path):
            self.modules.append(("DMARC Report Parser", os.path.relpath(dmarc_path, BASE)))
        
        # Add SKU module - we'll create it later
        sku_path = os.path.join(BASE, "pricing", "sku_manager.py")
        self.modules.append(("SKU Manager", os.path.relpath(sku_path, BASE)))
        
        for name, path in self.modules:
            btn = ttk.Button(self.modules_frame, text=name, command=lambda p=path, n=name: self.run_module(p, n))
            btn.pack(fill='x', pady=2)
            self.module_buttons.append(btn)
            if name == "Stock Level Checker":
                self.edit_stock_btn = ttk.Button(self.modules_frame, text="Edit Stock", command=self.edit_stock, state='disabled')
                self.edit_stock_btn.pack(fill='x', pady=2)

        # Right: output
        right = ttk.Frame(self)
        right.pack(side='right', expand=True, fill='both', padx=10, pady=10)

        ttk.Label(right, text="Output", font=(None, 12, 'bold')).pack(anchor='w')
        self.output = tk.Text(right, wrap='word')
        self.output.pack(expand=True, fill='both')

        clear = ttk.Button(right, text="Clear Output", command=lambda: self.output.delete('1.0','end'))
        clear.pack(anchor='e', pady=(5,0))

    def run_module(self, path, name):
        full_path = os.path.join(BASE, path)
        if not os.path.exists(full_path):
            messagebox.showerror('Not found', f'Script not found:\n{full_path}')
            return
        
        if name == "Stock Level Checker":
            self.edit_stock_btn.config(state='normal')
        elif name == "DMARC Report Parser":
            self.run_dmarc()
            return
        elif name == "SKU Manager":
            self.run_sku_manager()
            return
        
        # run in thread and capture output
        thread = threading.Thread(target=self._run_and_capture, args=(full_path,))
        thread.daemon = True
        thread.start()

    def run_selected(self):
        messagebox.showinfo('Select','Please click on a module button to run')

    def run_selected_bg(self):
        messagebox.showinfo('Select','Please click on a module button to run')

    def _run_and_capture(self, path):
        self._append_output(f"Running: {path}\n---\n")
        try:
            # Hide console window on Windows
            kwargs = {}
            if os.name == 'nt':
                import subprocess
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            proc = subprocess.run([sys.executable, path], capture_output=True, text=True, **kwargs)
            if proc.stdout:
                self._append_output(proc.stdout)
            if proc.stderr:
                self._append_output('\n[stderr]\n' + proc.stderr)
            self._append_output('\n--- Finished ---\n')
        except Exception as e:
            self._append_output(f"Error while running: {e}\n")

    def _append_output(self, text):
        def inner():
            self.output.insert('end', text)
            self.output.see('end')
        self.after(0, inner)

    def open_script(self):
        p = filedialog.askopenfilename(initialdir=BASE, filetypes=[('Python','*.py'),('All','*.*')])
        if p:
            # insert at end of list
            rel = os.path.relpath(p, BASE)
            self.module_list.insert('end', rel)

    def open_shopping_list(self):
        if os.path.exists(SHOPPING_LIST):
            self.open_file(SHOPPING_LIST)
        else:
            messagebox.showinfo('Not found', 'Shopping list not found. Run stock checker first.')

    def print_shopping_list(self):
        if os.path.exists(SHOPPING_LIST):
            try:
                if os.name == 'nt':
                    os.startfile(SHOPPING_LIST, 'print')
                else:
                    # For Linux/Mac, use lpr or similar
                    subprocess.Popen(['lpr', SHOPPING_LIST])
            except Exception as e:
                messagebox.showerror('Error', f'Print failed: {e}')
        else:
            messagebox.showinfo('Not found', 'Shopping list not found. Run stock checker first.')

    def edit_stock(self):
        stock_file = os.path.join(BASE, "stock", "stock_levels.csv")
        if not os.path.exists(stock_file):
            messagebox.showerror('Not found', 'Stock file not found.')
            return
        
        # Load stock data
        stock_data = []
        with open(stock_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stock_data.append({
                    'item': row['item'],
                    'quantity': int(row['quantity']),
                    'minimum': int(row['minimum'])
                })
        
        # Create edit window
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Stock Levels")
        edit_win.geometry("500x400")
        
        # Listbox for items
        listbox = tk.Listbox(edit_win, width=50, height=15)
        listbox.pack(pady=10)
        
        for item in stock_data:
            listbox.insert('end', f"{item['item']} - Qty: {item['quantity']}, Min: {item['minimum']}")
        
        # Buttons
        btn_frame = ttk.Frame(edit_win)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Add Item", command=lambda: self.add_stock_item(edit_win, listbox, stock_data)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit Item", command=lambda: self.edit_stock_item(edit_win, listbox, stock_data)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Item", command=lambda: self.delete_stock_item(listbox, stock_data)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Save", command=lambda: self.save_stock(stock_data, stock_file, edit_win)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=edit_win.destroy).pack(side='left', padx=5)

    def add_stock_item(self, parent, listbox, stock_data):
        add_win = tk.Toplevel(parent)
        add_win.title("Add Stock Item")
        add_win.geometry("300x150")
        
        ttk.Label(add_win, text="Item Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(add_win)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Quantity:").grid(row=1, column=0, padx=5, pady=5)
        qty_entry = ttk.Entry(add_win)
        qty_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Minimum:").grid(row=2, column=0, padx=5, pady=5)
        min_entry = ttk.Entry(add_win)
        min_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            try:
                name = name_entry.get().strip()
                qty = int(qty_entry.get())
                min_qty = int(min_entry.get())
                if name:
                    stock_data.append({'item': name, 'quantity': qty, 'minimum': min_qty})
                    listbox.insert('end', f"{name} - Qty: {qty}, Min: {min_qty}")
                    add_win.destroy()
                else:
                    messagebox.showerror('Error', 'Item name cannot be empty.')
            except ValueError:
                messagebox.showerror('Error', 'Quantity and minimum must be numbers.')
        
        ttk.Button(add_win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def edit_stock_item(self, parent, listbox, stock_data):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo('Select', 'Please select an item to edit.')
            return
        index = sel[0]
        item = stock_data[index]
        
        edit_win = tk.Toplevel(parent)
        edit_win.title("Edit Stock Item")
        edit_win.geometry("300x150")
        
        ttk.Label(edit_win, text="Item Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(edit_win)
        name_entry.insert(0, item['item'])
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Quantity:").grid(row=1, column=0, padx=5, pady=5)
        qty_entry = ttk.Entry(edit_win)
        qty_entry.insert(0, str(item['quantity']))
        qty_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Minimum:").grid(row=2, column=0, padx=5, pady=5)
        min_entry = ttk.Entry(edit_win)
        min_entry.insert(0, str(item['minimum']))
        min_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            try:
                name = name_entry.get().strip()
                qty = int(qty_entry.get())
                min_qty = int(min_entry.get())
                if name:
                    stock_data[index] = {'item': name, 'quantity': qty, 'minimum': min_qty}
                    listbox.delete(index)
                    listbox.insert(index, f"{name} - Qty: {qty}, Min: {min_qty}")
                    edit_win.destroy()
                else:
                    messagebox.showerror('Error', 'Item name cannot be empty.')
            except ValueError:
                messagebox.showerror('Error', 'Quantity and minimum must be numbers.')
        
        ttk.Button(edit_win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_stock_item(self, listbox, stock_data):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo('Select', 'Please select an item to delete.')
            return
        index = sel[0]
        if messagebox.askyesno('Confirm', 'Delete this item?'):
            del stock_data[index]
            listbox.delete(index)

    def save_stock(self, stock_data, file_path, edit_win):
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['item', 'quantity', 'minimum'])
                writer.writeheader()
                for item in stock_data:
                    writer.writerow(item)
            messagebox.showinfo('Saved', 'Stock levels saved successfully.')
            edit_win.destroy()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save: {e}')

    def run_dmarc(self):
        dmarc_win = tk.Toplevel(self)
        dmarc_win.title("DMARC Report Processor")
        dmarc_win.geometry("400x200")
        
        ttk.Label(dmarc_win, text="DMARC Report Parser", font=(None, 14, 'bold')).pack(pady=10)
        ttk.Label(dmarc_win, text="Upload a DMARC report file to process.").pack(pady=5)
        
        upload_btn = ttk.Button(dmarc_win, text="Upload Report", command=lambda: self.upload_dmarc_report(dmarc_win))
        upload_btn.pack(pady=10)
        
        ttk.Button(dmarc_win, text="Close", command=dmarc_win.destroy).pack(pady=5)

    def upload_dmarc_report(self, parent_win):
        reports_dir = os.path.join(BASE, "security", "dmarc", "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        file_path = filedialog.askopenfilename(title="Select DMARC Report", filetypes=[("XML files", "*.xml"), ("GZ files", "*.gz"), ("All files", "*.*")])
        if not file_path:
            return
        
        # Copy file to reports folder
        import shutil
        filename = os.path.basename(file_path)
        dest_path = os.path.join(reports_dir, filename)
        shutil.copy(file_path, dest_path)
        
        # Run the parser
        thread = threading.Thread(target=self._run_dmarc_parser, args=(dest_path,))
        thread.daemon = True
        thread.start()
        
        parent_win.destroy()

    def run_sku_manager(self):
        sku_win = tk.Toplevel(self)
        sku_win.title("SKU Manager")
        sku_win.geometry("600x400")
        
        # Listbox for SKUs
        listbox = tk.Listbox(sku_win, width=80, height=15)
        listbox.pack(pady=10)
        
        # Load and display SKUs
        sku_file = os.path.join(BASE, "pricing", "skus.json")
        skus = []
        if os.path.exists(sku_file):
            with open(sku_file, 'r') as f:
                skus = json.load(f)
        
        for sku in skus:
            listbox.insert('end', f"{sku['sku']} - {sku['name']}")
        
        # Buttons
        btn_frame = ttk.Frame(sku_win)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Add SKU", command=lambda: self.add_sku(sku_win, listbox, skus)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Edit SKU", command=lambda: self.edit_sku(sku_win, listbox, skus)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete SKU", command=lambda: self.delete_sku(listbox, skus)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Save", command=lambda: self.save_skus(skus, sku_file, sku_win)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=sku_win.destroy).pack(side='left', padx=5)

    def add_sku(self, parent, listbox, skus):
        add_win = tk.Toplevel(parent)
        add_win.title("Add SKU")
        add_win.geometry("400x250")
        
        ttk.Label(add_win, text="SKU:").grid(row=0, column=0, padx=5, pady=5)
        sku_entry = ttk.Entry(add_win)
        sku_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(add_win)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Description:").grid(row=2, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(add_win)
        desc_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(add_win, text="Materials (comma separated):").grid(row=3, column=0, padx=5, pady=5)
        mat_entry = ttk.Entry(add_win)
        mat_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def save():
            sku = sku_entry.get().strip()
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            mats = [m.strip() for m in mat_entry.get().split(',') if m.strip()]
            if sku and name:
                skus.append({'sku': sku, 'name': name, 'description': desc, 'materials': mats})
                listbox.insert('end', f"{sku} - {name}")
                add_win.destroy()
            else:
                messagebox.showerror('Error', 'SKU and Name are required.')
        
        ttk.Button(add_win, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_sku(self, parent, listbox, skus):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo('Select', 'Please select an SKU to edit.')
            return
        index = sel[0]
        sku_data = skus[index]
        
        edit_win = tk.Toplevel(parent)
        edit_win.title("Edit SKU")
        edit_win.geometry("400x250")
        
        ttk.Label(edit_win, text="SKU:").grid(row=0, column=0, padx=5, pady=5)
        sku_entry = ttk.Entry(edit_win)
        sku_entry.insert(0, sku_data['sku'])
        sku_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(edit_win)
        name_entry.insert(0, sku_data['name'])
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Description:").grid(row=2, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(edit_win)
        desc_entry.insert(0, sku_data['description'])
        desc_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(edit_win, text="Materials (comma separated):").grid(row=3, column=0, padx=5, pady=5)
        mat_entry = ttk.Entry(edit_win)
        mat_entry.insert(0, ', '.join(sku_data['materials']))
        mat_entry.grid(row=3, column=1, padx=5, pady=5)
        
        def save():
            sku = sku_entry.get().strip()
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            mats = [m.strip() for m in mat_entry.get().split(',') if m.strip()]
            if sku and name:
                skus[index] = {'sku': sku, 'name': name, 'description': desc, 'materials': mats}
                listbox.delete(index)
                listbox.insert(index, f"{sku} - {name}")
                edit_win.destroy()
            else:
                messagebox.showerror('Error', 'SKU and Name are required.')
        
        ttk.Button(edit_win, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_sku(self, listbox, skus):
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo('Select', 'Please select an SKU to delete.')
            return
        index = sel[0]
        if messagebox.askyesno('Confirm', 'Delete this SKU?'):
            del skus[index]
            listbox.delete(index)

    def save_skus(self, skus, file_path, sku_win):
        with open(file_path, 'w') as f:
            json.dump(skus, f, indent=4)
        messagebox.showinfo('Saved', 'SKUs saved successfully.')
        sku_win.destroy()

    def _run_dmarc_parser(self, file_path):
        self._append_output(f"Processing DMARC report: {file_path}\n---\n")
        try:
            # Import and run the parser
            import importlib.util
            dmarc_path = os.path.join(BASE, "security", "dmarc", "dmarc_parser.py")
            spec = importlib.util.spec_from_file_location("dmarc_parser", dmarc_path)
            dmarc_parser = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(dmarc_parser)
            
            records = dmarc_parser.parse_dmarc(file_path)
            summary_records = dmarc_parser.summarize_by_ip(records)
            
            # Export to CSV
            filename = f"summary_{os.path.basename(file_path).replace('.xml', '').replace('.gz', '')}.csv"
            dmarc_parser.export_to_csv(summary_records, filename)
            
            self._append_output(f"Summary saved to dmarc_summaries/{filename}\n")
            self._append_output("Processing complete.\n")
        except Exception as e:
            self._append_output(f"Error processing DMARC report: {e}\n")


if __name__ == '__main__':
    app = App()
    app.mainloop()
