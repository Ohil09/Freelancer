# Freelancer Management System - Database Connection Guide

## Overview
This guide provides step-by-step instructions on how to set up and connect to the database for the Freelancer Time and Invoice Management System.

## Database Technology
- **Type**: SQLite3 (File-based database)
- **File Location**: `database.db` (automatically created in the project root)
- **No Server Required**: SQLite runs as a library embedded in Python

---

## Step 1: Prerequisites

### System Requirements
- Python 3.8 or higher
- pip (Python Package Manager)
- 20 MB free disk space

### Verify Python Installation
```bash
python --version
# or
python3 --version
```

If Python is not installed, download from: https://www.python.org/downloads/

---

## Step 2: Install Dependencies

### Option A: Using requirements.txt (Recommended)
```bash
# Navigate to project directory
cd /path/to/Freelancer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Install Flask and dependencies
pip install -r requirements.txt
```

### Option B: Manual Installation
```bash
pip install Flask==2.3.3 Werkzeug==2.3.7
```

---

## Step 3: Initialize Database

### Automatic Initialization (On First Run)
When you run the Flask application for the first time, the database will automatically initialize:

```bash
python app.py
```

The `init_database()` function in `database.py` will automatically create all required tables.

### Manual Database Initialization
If you need to manually initialize the database:

```bash
python database.py
```

Expected output:
```
✓ Database initialized successfully!
```

---

## Step 4: Database Structure

### Tables Created

#### 1. **users** - User Accounts
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL (admin/freelancer),
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
)
```

#### 2. **projects** - Project Information
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    rate REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    user_id INTEGER NOT NULL (Foreign Key),
    deadline TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 3. **time_logs** - Work Hours Tracking
```sql
CREATE TABLE time_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL (Foreign Key),
    user_id INTEGER NOT NULL (Foreign Key),
    hours REAL NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
)
```

#### 4. **project_updates** - Project Task Updates
```sql
CREATE TABLE project_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL (Foreign Key),
    user_id INTEGER NOT NULL (Foreign Key),
    completed_tasks TEXT NOT NULL,
    pending_tasks TEXT NOT NULL,
    progress INTEGER NOT NULL,
    remarks TEXT,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 5. **progress_updates** - Detailed Progress Tracking
```sql
CREATE TABLE progress_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL (Foreign Key),
    user_id INTEGER NOT NULL (Foreign Key),
    progress INTEGER NOT NULL,
    completed_tasks TEXT NOT NULL,
    remaining_work TEXT NOT NULL,
    remarks TEXT,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 6. **invoice_requests** - Invoice Management
```sql
CREATE TABLE invoice_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL (Foreign Key),
    user_id INTEGER NOT NULL (Foreign Key),
    status TEXT NOT NULL DEFAULT 'Pending',
    total_hours REAL,
    total_amount REAL,
    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### 7. **payments** - Payment Records
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    project_id INTEGER NOT NULL (Foreign Key),
    user_id INTEGER NOT NULL (Foreign Key),
    amount REAL NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'Pending',
    payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## Step 5: Add Initial Admin User

### Create Default Admin Account

Create a file named `init_admin.py` in the project root:

```python
from database import get_db_connection, close_db_connection

def create_admin():
    conn = get_db_connection()
    
    # Check if admin already exists
    existing = conn.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    ).fetchone()
    
    if existing:
        print("Admin user already exists!")
        close_db_connection(conn)
        return
    
    # Create admin user
    conn.execute(
        "INSERT INTO users(username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin123", "admin")
    )
    conn.commit()
    close_db_connection(conn)
    
    print("✓ Admin user created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
    print("  WARNING: Change password after first login!")

if __name__ == "__main__":
    create_admin()
```

Run the script:
```bash
python init_admin.py
```

---

## Step 6: Running the Application

### Start the Flask Server

```bash
# Activate virtual environment first (if not already active)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run the application
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000/login
```

### Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

---

## Step 7: Database Connectivity Code Reference

### Database Connection Function (from `database.py`)

```python
def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
```

### Example Query Usage in Flask Routes

```python
from database import get_db_connection, close_db_connection

# Example: Get all users
conn = get_db_connection()
users = conn.execute("SELECT * FROM users").fetchall()
close_db_connection(conn)

# Example: Insert a new project
conn = get_db_connection()
conn.execute(
    "INSERT INTO projects(name, type, rate, status, user_id, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
    ("Project Name", "Web Development", 50.0, "Active", 1)
)
conn.commit()
close_db_connection(conn)
```

---

## Step 8: Backup and Recovery

### Backup Database

```bash
# Simple file copy (Windows)
copy database.db database_backup.db

# Or (Linux/Mac)
cp database.db database_backup.db
```

### Restore from Backup

```bash
# Windows
copy database_backup.db database.db

# Linux/Mac
cp database_backup.db database.db
```

### Delete Database (Reset)

```bash
# Remove the database file
rm database.db  # Linux/Mac
del database.db  # Windows PowerShell
```

The database will be recreated automatically on next run.

---

## Step 9: Troubleshooting

### Issue: "database.db not found"
**Solution**: The database will be created automatically when you run `app.py`. If it's not creating:
```bash
python database.py
```

### Issue: "Users table doesn't exist"
**Solution**: Reinitialize the database:
```bash
python database.py
```

### Issue: "Cannot import database module"
**Solution**: Ensure you're in the project directory:
```bash
cd /path/to/Freelancer
python app.py
```

### Issue: "Port 5000 already in use"
**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, host="0.0.0.0", port=5001)  # Change 5000 to 5001
```

### Issue: "Permission denied to database.db"
**Solution**: Check file permissions:
```bash
# Linux/Mac
chmod 644 database.db

# Windows: Right-click → Properties → Security → Edit
```

---

## Step 10: Upgrade to Different Database (Future)

### Migrate to MySQL
When scaling beyond SQLite, modify the connection in `database.py`:

```python
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        ******,
        database="freelancer_db"
    )
```

### Migrate to PostgreSQL
```python
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="freelancer_db",
        user="postgres",
        ******
    )
```

---

## Database Schema Diagram

```
users (One-to-Many)
  ├─→ projects
  ├─→ time_logs
  ├─→ project_updates
  ├─→ progress_updates
  ├─→ invoice_requests
  └─→ payments

projects (One-to-Many)
  ├─→ time_logs
  ├─→ project_updates
  ├─→ progress_updates
  ├─→ invoice_requests
  └─→ payments
```

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Change Admin Password**: After first login, change the default admin password
2. **Password Hashing**: Consider implementing password hashing (bcrypt) for production
3. **Environment Variables**: Store sensitive data in `.env` file, not in code
4. **Database Encryption**: SQLite does not have built-in encryption; use encrypted filesystems for production
5. **Connection Pooling**: For high traffic, implement connection pooling

---

## Performance Tips

- **Indexing**: Add indexes on frequently queried columns
- **Connection Pooling**: Use `sqlalchemy` for better connection management
- **Query Optimization**: Avoid N+1 queries, use JOINs
- **Caching**: Implement caching for frequently accessed data

---

## Summary

| Step | Command | Purpose |
|------|---------|---------|
| 1 | `python -m venv venv` | Create virtual environment |
| 2 | `source venv/bin/activate` | Activate environment |
| 3 | `pip install -r requirements.txt` | Install dependencies |
| 4 | `python database.py` | Initialize database |
| 5 | `python init_admin.py` | Create admin user |
| 6 | `python app.py` | Run application |
| 7 | Visit `http://localhost:5000/login` | Access application |

---

## Additional Resources

- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Python sqlite3 Module**: https://docs.python.org/3/library/sqlite3.html

---

**Last Updated**: 2024
**Version**: 2.0
**Status**: Ready for Development
