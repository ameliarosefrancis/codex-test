DMARC Parser Script README
==========================

Purpose
-------
Parses DMARC XML reports (.gz files) from reports/ folder, summarizes email authentication results by IP, and exports to CSV and Excel.

Usage
-----
Run the script directly:
python dmarc_parser.py

It processes all .gz files in reports/, generates summaries.

Output
------
- CSV summary: IP, total messages, passes, fails, compliance %.
- Excel report with raw and summary data.

Files Used
----------
- reports/*.gz: DMARC XML reports.
- dmarc_summaries/: Output folder for CSV and XLSX.

Dependencies
------------
- openpyxl for Excel export.

Notes
-----
- Handles compressed XML.
- Compliance based on DKIM and SPF pass.