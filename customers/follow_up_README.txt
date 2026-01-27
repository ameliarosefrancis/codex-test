Customer Follow-Up Script README
================================

Purpose
-------
Generates follow-up messages for customers using templates (ready for pickup, thank you, check-in). Logs contacts to CSV.

Usage
-----
Run the script directly:
python follow_up.py

Prompts for customer name, order, contact method, and message type.

Templates
---------
- ready_for_pickup.txt
- thank_you.txt
- check_in.txt

Output
------
- Displays generated message.
- Logs to customer_log.csv: name, order, method, timestamp.

Files Used
----------
- customer_log.csv: Contact log.
- templates/*.txt: Message templates with {name} and {order} placeholders.

Notes
-----
- Interactive; requires inputs.
- Templates must exist in templates/ folder.