import sqlite3

conn = sqlite3.connect('database.db')

def add_column(table, column, col_type):
    cols = [row[1] for row in conn.execute(f'PRAGMA table_info({table})')]
    if column not in cols:
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
        print(f'Added {table}.{column}')
    else:
        print(f'Skipped {table}.{column} (already exists)')

add_column('invoice_requests', 'total_hours', 'REAL')
add_column('invoice_requests', 'total_amount', 'REAL')
add_column('invoice_requests', 'requested_date', 'TIMESTAMP')
add_column('payments', 'invoice_id', 'INTEGER')
add_column('payments', 'payment_date', 'TIMESTAMP')
add_column('payments', 'created_at', 'TIMESTAMP')

conn.execute("UPDATE invoice_requests SET requested_date = CURRENT_TIMESTAMP WHERE requested_date IS NULL")
conn.execute("UPDATE payments SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

conn.commit()
conn.close()
print('All done')