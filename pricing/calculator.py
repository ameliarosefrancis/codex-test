import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE, "pricing_log.csv")

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def calculate_price():
    print("\n=== Pricing Calculator ===\n")

    material_cost = get_float("Material cost ($): ")
    time_minutes = get_float("Time required (minutes): ")
    hourly_rate = get_float("Your hourly rate ($/hr): ")
    packaging_cost = get_float("Packaging cost ($): ")
    extras = get_float("Extra costs (magnets, ribbon, hooks, etc.) ($): ")

    # Convert minutes to hours
    time_hours = time_minutes / 60

    labour_cost = time_hours * hourly_rate
    total_cost = material_cost + labour_cost + packaging_cost + extras

    # Recommended retail price (your margin target)
    recommended_price = total_cost * 1.4  # 40% margin
    minimum_price = total_cost * 1.15     # 15% margin

    print("\n=== Results ===")
    print(f"Material Cost:       ${material_cost:.2f}")
    print(f"Labour Cost:         ${labour_cost:.2f}")
    print(f"Packaging Cost:      ${packaging_cost:.2f}")
    print(f"Extras:              ${extras:.2f}")
    print(f"--------------------------------")
    print(f"Total Cost:          ${total_cost:.2f}")
    print(f"Minimum Price (15%): ${minimum_price:.2f}")
    print(f"Recommended Price:   ${recommended_price:.2f}")

    # Save to log
    save = input("\nSave this quote to your log? (y/n): ").strip().lower()
    if save == "y":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp},{material_cost},{labour_cost},{packaging_cost},{extras},{total_cost},{minimum_price},{recommended_price}\n")
        print("Quote saved.")

    input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    calculate_price()