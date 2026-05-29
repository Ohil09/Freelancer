"""
Initialize Admin User for Freelancer Management System

This script creates the default admin user for the system.
Run this after first database setup.
"""

from database import get_db_connection, close_db_connection, init_database


def create_admin():
    """Create default admin user"""
    try:
        # Initialize database first
        init_database()
        
        conn = get_db_connection()
        
        # Check if admin already exists
        existing = conn.execute(
            "SELECT * FROM users WHERE username=?",
            ("admin",)
        ).fetchone()
        
        if existing:
            print("✓ Admin user already exists!")
            print(f"  ID: {existing['id']}")
            print(f"  Username: {existing['username']}")
            close_db_connection(conn)
            return False
        
        # Create admin user
        conn.execute(
            "INSERT INTO users(username, password, role, email) VALUES (?, ?, ?, ?)",
            ("admin", "admin123", "admin", "admin@example.com")
        )
        conn.commit()
        close_db_connection(conn)
        
        print("✓ Admin user created successfully!")
        print("\n  Login Credentials:")
        print("  ==================")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: Admin")
        print("\n  WARNING: Change the password after first login!")
        print("  NEVER share admin credentials!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        return False


if __name__ == "__main__":
    print("Initializing Admin User for Freelancer Management System")
    print("=" * 55)
    create_admin()
