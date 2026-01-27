import os
import sys
import subprocess

# Paths to your modules
BASE = os.path.dirname(os.path.abspath(__file__))

MODULES = {
    "1": ("Order Intake & Prep Bot", os.path.join(BASE, "order_intake", "watcher.py")),
    "2": ("Pricing Calculator", os.path.join(BASE, "pricing", "calculator.py")),
    "3": ("Stock Level Checker", os.path.join(BASE, "stock", "stock_checker.py")),
    "4": ("Customer Follow-Up Bot", os.path.join(BASE, "customers", "follow_up.py")),
    "5": ("Maintenance Reminder Bot", os.path.join(BASE, "maintenance", "reminders.py")),
    "6": ("DMARC Report Parser", os.path.join(BASE, "security", "dmarc", "dmarc_parser.py")),
    "7": ("Exit", None)
}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def run_module(path):
    if not os.path.exists(path):
        print(f"\n⚠️ Module not found: {path}")
        return
    print(f"\n▶ Running: {path}\n")
    # run with the same interpreter as the hub
    subprocess.run([sys.executable, path])
    # pause after module finishes
    input("\nPress Enter to return to the menu...")

def main():
    while True:
        clear_screen()
        print("=======================================")
        print("   AmeliaRose Business Automation Hub   ")
        print("=======================================\n")

        for key, (name, _) in MODULES.items():
            print(f"{key}. {name}")

        choice = input("\nSelect an option: ").strip()

        if choice not in MODULES:
            print("\nInvalid choice. Try again.")
            input("Press Enter to continue...")
            continue

        name, path = MODULES[choice]

        if choice == "7":
            print("\nGoodbye!")
            break

        print(f"\nYou selected: {name}")
        run_module(path)

if __name__ == "__main__":
    main()