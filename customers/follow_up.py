import os
import csv
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE, "customer_log.csv")
TEMPLATE_DIR = os.path.join(BASE, "templates")

TEMPLATES = {
    "1": ("Order Ready for Pickup", "ready_for_pickup.txt"),
    "2": ("Thank You Message", "thank_you.txt"),
    "3": ("Check-In Message", "check_in.txt")
}

def load_template(filename):
    path = os.path.join(TEMPLATE_DIR, filename)
    with open(path, "r") as f:
        return f.read()

def log_contact(name, order, method):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, order, method, timestamp])

def follow_up():
    print("\n=== Customer Follow-Up Bot ===\n")

    name = input("Customer name: ").strip()
    order = input("Order description: ").strip()
    contact_method = input("Contact method (Messenger/SMS/Email): ").strip()

    print("\nChoose message type:")
    for key, (label, _) in TEMPLATES.items():
        print(f"{key}. {label}")

    choice = input("\nSelect an option: ").strip()

    if choice not in TEMPLATES:
        print("Invalid choice.")
        input("\nPress Enter to return to the menu...")
        return

    label, filename = TEMPLATES[choice]
    template = load_template(filename)

    message = template.format(name=name, order=order)

    print("\n--- Generated Message ---\n")
    print(message)
    print("\n-------------------------\n")

    log_contact(name, order, contact_method)
    print("Follow-up logged.")

    input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    follow_up()