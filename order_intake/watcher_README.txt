Order Intake Watcher Script README
=================================

Purpose
-------
This script monitors the Orders_Inbox folder for new order files (.txt or .eml), extracts order details using regex patterns, and creates job cards in JSON and TXT formats in the To_Cut folder. Processed files are moved to Processed_Orders.

Usage
-----
Run the script directly:
python watcher.py

It runs continuously, checking every 5 seconds. Use CTRL+C to stop.

Or use the GUI launcher to run it in background.

Folders
-------
- Orders_Inbox: Place new order files here.
- To_Cut: Output job cards (.json and .txt).
- Processed_Orders: Moved processed files.

Extraction Patterns
-------------------
- Customer: "Customer: ..."
- Product: "Product: ..."
- Material: "Material: ..."
- Due Date: "Due: ..."
- Notes: "Notes: ..."

Output
------
- JSON file with all details and timestamp.
- TXT summary file.
- Console log of processed files.

Notes
-----
- Runs in a loop; suitable for background execution.
- Handles text files with errors ignored.