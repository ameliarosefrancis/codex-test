Stock Checker Script README
==========================

Purpose
-------
This script checks current stock levels against minimum thresholds and identifies items that need restocking. It displays all stock levels with status (OK/LOW) and automatically generates a shopping list for low items.

Usage
-----
Run the script directly:
python stock_checker.py

Or use the GUI launcher (app_gui.py) and select "Stock Level Checker".

Output
------
- Lists all items with current quantity, minimum required, and status.
- Highlights items below minimum as needing restock.
- Saves a shopping list to shopping_list.txt with timestamp.

Files Used
----------
- stock_levels.csv: Contains item, quantity, minimum columns.
- shopping_list.txt: Output file for restock items.

Notes
-----
- Quantities and minimums are integers.
- Shopping list is overwritten each run.
- No user input required; runs automatically.