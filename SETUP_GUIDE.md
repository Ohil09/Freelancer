# Quick Setup Guide - Freelancer Management System

This guide provides the fastest way to get the application running.

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.8 or higher installed
- Git (optional, if cloning from GitHub)

### Steps

#### 1. Navigate to Project Directory
```bash
cd /path/to/Freelancer
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Initialize Database
```bash
python database.py
```

Expected output: `✓ Database initialized successfully!`

#### 5. Create Admin User
```bash
python init_admin.py
```

#### 6. Run Application
```bash
python app.py
```

#### 7. Access Application
Open your browser: **http://localhost:5000/login**

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

---

## 🔧 Troubleshooting

### Module Not Found Error
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Port 5000 Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Database Already Exists
```bash
# Delete old database (warning: deletes all data!)
rm database.db  # Linux/Mac
del database.db # Windows

# Reinitialize
python database.py
python init_admin.py
```

---

## 📁 File Organization

| File/Folder | Purpose |
|------------|---------|
| `app.py` | Main Flask application |
| `database.py` | Database setup and connection |
| `init_admin.py` | Create admin user |
| `requirements.txt` | Python dependencies |
| `templates/` | HTML templates |
| `static/` | CSS and JavaScript files |
| `database.db` | SQLite database (auto-created) |

---

## 🚀 After Setup

1. **Change Admin Password**: Login and update password immediately
2. **Create Freelancer Users**: Use Manage Users to add accounts
3. **Start Using**: Create projects and manage freelancers

---

## 📚 Need More Help?

- Full Setup Guide: See `DATABASE_CONNECTION_GUIDE.md`
- System Features: See `README.md`
- Dependencies: See `requirements.py`

---

## Environment Variables (Optional)

Enable debug mode during development:
```bash
# Windows
set FLASK_DEBUG=True
python app.py

# Linux/Mac
export FLASK_DEBUG=True
python app.py
```

---

**Version**: 2.0 | **Status**: Ready to Use
