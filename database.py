"""
Database Module for Freelancer Management System
Handles all database connections and initialization
"""

import sqlite3
import os

DATABASE_PATH = "database.db"


def get_db_connection():
    """
    Create and return a database connection.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    Initialize the database with all required tables.
    Creates tables if they don't already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table - stores user account information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'freelancer')),
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive'))
        )
    """)
    
    # Projects table - stores project information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            rate REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive', 'Completed')),
            user_id INTEGER NOT NULL,
            deadline TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Time logs table - records work hours
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            hours REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Project updates table - tracks task progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            completed_tasks TEXT NOT NULL,
            pending_tasks TEXT NOT NULL,
            progress INTEGER NOT NULL CHECK(progress >= 0 AND progress <= 100),
            remarks TEXT,
            update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Progress updates table - detailed progress tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            progress INTEGER NOT NULL CHECK(progress >= 0 AND progress <= 100),
            completed_tasks TEXT NOT NULL,
            remaining_work TEXT NOT NULL,
            remarks TEXT,
            update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Invoice requests table - manages invoice requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected')),
            total_hours REAL,
            total_amount REAL,
            requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Payments table - tracks payment records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_status TEXT NOT NULL DEFAULT 'Pending' CHECK(payment_status IN ('Pending', 'Completed', 'Failed')),
            payment_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    ensure_project_created_at(conn)
    
    conn.commit()
    conn.close()
    
    print("✓ Database initialized successfully!")


def ensure_project_created_at(conn):
    """
    Ensure projects table has all required columns.
    Also ensure users table has email, created_at, and status columns.
    """
    # Check and add missing columns to projects table
    columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)")}
    if "created_at" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN created_at TIMESTAMP")
        conn.execute(
            "UPDATE projects SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
        )
    if "deadline" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN deadline TEXT")
    if "description" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN description TEXT")

    # Time logs table migrations
    time_columns = {row[1] for row in conn.execute("PRAGMA table_info(time_logs)")}
    if "description" not in time_columns:
        conn.execute("ALTER TABLE time_logs ADD COLUMN description TEXT")

    # Check and add missing columns to users table
    user_columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    if "email" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "created_at" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        conn.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    if "status" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN status TEXT")
        conn.execute("UPDATE users SET status = 'active' WHERE status IS NULL")


def close_db_connection(conn):
    """
    Safely close a database connection.
    
    Args:
        conn (sqlite3.Connection): Database connection to close
    """
    if conn:
        conn.close()


def check_db_exists():
    """
    Check if the database file exists.
    
    Returns:
        bool: True if database exists, False otherwise
    """
    return os.path.exists(DATABASE_PATH)


if __name__ == "__main__":
    # Initialize database when script is run directly
    init_database()
