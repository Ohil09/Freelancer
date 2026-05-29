"""
init_admin.py
Creates the default admin user for the Freelancer Management System.
Run this after clear_data.py or on a fresh database.
"""

import sqlite3

conn = sqlite3.connect('database.db')

print("Initializing admin user...")
print("=" * 40)

try:
    # Check if admin already exists
    existing = conn.execute(
        "SELECT * FROM users WHERE username = ?", ("admin",)
    ).fetchone()

    if existing:
        print("✓ Admin user already exists, skipping.")
    else:
        conn.execute(
            "INSERT INTO users (username, password, role, email, status) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin123", "admin", "admin@example.com", "active")
        )
        conn.commit()
        print("✓ Admin user created successfully!")

    print("=" * 40)
    print("  Login Credentials:")
    print("  Username : admin")
    print("  Password : admin123")
    print("  Role     : Admin")
    print("=" * 40)
    print("  WARNING: Change the password after first login!")

except Exception as e:
    print(f"✗ Error creating admin user: {e}")

conn.close()