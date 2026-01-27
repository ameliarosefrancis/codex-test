import os
import csv
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
STOCK_FILE = os.path.join(BASE, "stock_levels.csv")
SHOPPING_LIST = os.path.join(BASE, "shopping_list.txt")

def load_stock():
    stock = []
    with open(STOCK_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stock.append({
                "item": row["item"],
                "quantity": int(row["quantity"]),
                "minimum": int(row["minimum"])
            })
    return stock

def check_stock():
    print("\n=== Stock Level Checker ===\n")

    stock = load_stock()
    low_items = []

    print("Current Stock Levels:\n")
    for item in stock:
        status = "LOW" if item["quantity"] < item["minimum"] else "OK"
        print(f"- {item['item']}: {item['quantity']} (min: {item['minimum']}) [{status}]")
        if item["quantity"] < item["minimum"]:
            low_items.append(item)

    print("\n" + "="*30)

    if not low_items:
        print("All stock levels look good!")
    else:
        print("Items that need restocking:\n")
        for item in low_items:
            print(f"- {item['item']} (Have {item['quantity']}, need at least {item['minimum']})")

        # For GUI mode, always save shopping list without prompting
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(SHOPPING_LIST, "w") as f:
            f.write(f"Shopping List - {timestamp}\n\n")
            for item in low_items:
                f.write(f"{item['item']} — Have {item['quantity']}, need {item['minimum']}\n")
        print(f"\nShopping list saved to {SHOPPING_LIST}")

    # Remove input to avoid hanging in GUI
    # input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    check_stock()