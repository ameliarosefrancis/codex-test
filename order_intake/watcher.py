import os
import json
import time
import re
from datetime import datetime

# Folder paths
BASE = os.path.dirname(os.path.abspath(__file__))
ORDERS_INBOX = os.path.join(BASE, "Orders_Inbox")
TO_CUT = os.path.join(BASE, "To_Cut")
PROCESSED = os.path.join(BASE, "Processed_Orders")

# Make sure folders exist
os.makedirs(ORDERS_INBOX, exist_ok=True)
os.makedirs(TO_CUT, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

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

def process_orders():
    print("Watching for new orders... (Press CTRL+C to stop)\n")
    while True:
        for filename in os.listdir(ORDERS_INBOX):
            if filename.lower().endswith((".txt", ".eml")):
                full_path = os.path.join(ORDERS_INBOX, filename)

                with open(full_path, "r", errors="ignore") as f:
                    text = f.read()

                details = extract_details(text)
                json_path, txt_path = create_job_card(details, filename)

                print(f"Processed: {filename}")
                print(f"Job card created: {json_path}")

                # Move original file to processed folder
                os.rename(full_path, os.path.join(PROCESSED, filename))

        time.sleep(5)

if __name__ == "__main__":
    process_orders()
    