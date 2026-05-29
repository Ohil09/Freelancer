"""
clear_data.py
Deletes all rows from every table while keeping the table structure intact.
Run this before handing the project to a new team member.
"""

import sqlite3

conn = sqlite3.connect('database.db')

tables = [
    'payments',
    'invoice_requests',
    'progress_updates',
    'project_updates',
    'time_logs',
    'projects',
    'users'
]

print("Clearing all table data...")
print("=" * 40)

for table in tables:
    try:
        conn.execute(f'DELETE FROM {table}')
        print(f'✓ Cleared {table}')
    except Exception as e:
        print(f'✗ Could not clear {table}: {e}')

# Reset auto-increment counters
conn.execute("DELETE FROM sqlite_sequence")

conn.commit()
conn.close()

print("=" * 40)
print("✓ All data cleared successfully!")
print("  Run init_admin.py next to create the admin user.")