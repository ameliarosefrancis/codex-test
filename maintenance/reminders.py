import os
import csv
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE, "maintenance_log.csv")

def load_tasks():
    tasks = []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append({
                "task": row["task"],
                "last_done": datetime.strptime(row["last_done"], "%Y-%m-%d"),
                "interval_days": int(row["interval_days"])
            })
    return tasks

def save_tasks(tasks):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["task", "last_done", "interval_days"])
        for t in tasks:
            writer.writerow([
                t["task"],
                t["last_done"].strftime("%Y-%m-%d"),
                t["interval_days"]
            ])

def check_maintenance():
    print("\n=== Maintenance Reminder Bot ===\n")

    tasks = load_tasks()
    today = datetime.now().date()
    due_tasks = []

    for t in tasks:
        next_due = t["last_done"].date() + timedelta(days=t["interval_days"])
        if today >= next_due:
            due_tasks.append((t, next_due))

    if not due_tasks:
        print("All maintenance tasks are up to date.")
    else:
        print("Tasks that need attention:\n")
        for t, next_due in due_tasks:
            print(f"- {t['task']} (Last done: {t['last_done'].date()}, Due: {next_due})")

        update = input("\nMark tasks as completed? (y/n): ").strip().lower()
        if update == "y":
            for t, _ in due_tasks:
                t["last_done"] = datetime.now()
            save_tasks(tasks)
            print("Tasks updated.")

    input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    check_maintenance()