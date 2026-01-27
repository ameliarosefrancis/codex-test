Maintenance Reminders Script README
==================================

Purpose
-------
Checks maintenance tasks against their intervals and identifies overdue tasks. Allows marking tasks as completed.

Usage
-----
Run the script directly:
python reminders.py

Loads tasks from maintenance_log.csv, checks dates, lists due tasks.

Files Used
----------
- maintenance_log.csv: task, last_done (YYYY-MM-DD), interval_days.

Output
------
- Lists overdue tasks with dates.
- Option to mark as completed, updating the log.

Notes
-----
- Interactive; prompts for update.
- Dates in YYYY-MM-DD format.