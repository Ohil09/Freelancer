# Freelancer Time and Invoice Management System

A comprehensive web-based application for managing freelancer projects, tracking work hours, monitoring productivity, and managing invoices with admin controls.

## 📋 Features

### User Module (Freelancers)
- **User Dashboard**: Overview of projects, hours, and earnings
- **Project Management**: Create, edit, and manage multiple projects
- **Time Tracking**: Log work hours for each project
- **Progress Updates**: Submit detailed progress reports
- **Invoice Requests**: Request invoice generation after project completion
- **Payment Tracking**: View payment status and history

### Admin Module
- **Admin Dashboard**: System overview and statistics
- **User Management**: Add, edit, and manage freelancer accounts
- **Project Monitoring**: Track all projects and their progress
- **Activity Tracking**: Monitor freelancer work hours and activity
- **Invoice Approval**: Review and approve/reject invoice requests
- **Payment Management**: Track and update payment status
- **Productivity Reports**: Generate productivity analytics

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3 (with Tailwind CSS)
- JavaScript (ES6)

### Backend
- Python 3.8+
- Flask 2.3.3

### Database
- SQLite3 (File-based)
- No database server required

### Development Tools
- VS Code
- Git
- Python pip

## 📦 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ohil09/Freelancer.git
cd Freelancer
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python database.py
```

### Step 5: Create Admin User
```bash
python init_admin.py
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change the password immediately after first login!**

### Step 6: Run the Application
```bash
python app.py
```

The application will start at: **http://localhost:5000**

## 🚀 Quick Start

1. **Login** with admin credentials at http://localhost:5000/login
2. **Create Users**: Go to Manage Users to add freelancer accounts
3. **Create Projects**: Add projects for freelancers to work on
4. **Track Time**: Freelancers can log their work hours
5. **Monitor Progress**: Track project updates and productivity
6. **Manage Invoices**: Approve invoices and process payments

## 📂 Project Structure

```
Freelancer/
├── app.py                          # Main Flask application
├── database.py                     # Database initialization and management
├── init_admin.py                   # Admin user creation script
├── requirements.py                 # Detailed requirements documentation
├── requirements.txt                # Python dependencies
├── DATABASE_CONNECTION_GUIDE.md    # Complete database setup guide
├── README.md                       # This file
├── database.db                     # SQLite database (auto-created)
├── templates/                      # HTML templates
├── static/                         # CSS and JavaScript files
└── venv/                          # Virtual environment
```

## 🗄️ Database Schema

The system uses SQLite with 7 tables:

1. **users** - User accounts and authentication
2. **projects** - Project information and details
3. **time_logs** - Work hours tracking
4. **project_updates** - Task and progress updates
5. **progress_updates** - Detailed progress tracking
6. **invoice_requests** - Invoice management
7. **payments** - Payment records and status

See `DATABASE_CONNECTION_GUIDE.md` for detailed schema information.

## 🔐 Security Features

- ✓ Role-based access control (Admin/Freelancer)
- ✓ Session management
- ✓ Login authentication
- ✓ Data validation on all forms
- ✓ SQL injection prevention using parameterized queries
- ✓ Error handling without exposing sensitive information

## ⚙️ Configuration

### Change Port
Edit `app.py` at the bottom:
```python
app.run(debug=False, host="0.0.0.0", port=5001)  # Change port to 5001
```

### Enable Debug Mode (Development)
```bash
export FLASK_DEBUG=True
python app.py
```

## 📚 API Routes

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /` - Main dashboard (role-based)

### Projects
- `GET /projects` - List projects
- `GET/POST /add_project` - Add new project
- `GET/POST /edit_project/<id>` - Edit project
- `GET /delete_project/<id>` - Delete project

### Time Tracking
- `GET/POST /time_tracking` - Log working hours

### Progress
- `GET/POST /project_progress` - Update project progress

### Invoices
- `GET /invoices` - View invoices
- `GET /approve_invoice/<id>` - Approve invoice (admin)
- `GET /reject_invoice/<id>` - Reject invoice (admin)

### Payments (Admin)
- `GET /payments` - View payment records
- `GET /update_payment_status/<id>/<status>` - Update payment status

### User Management (Admin)
- `GET/POST /manage_users` - Manage user accounts
- `GET /delete_user/<id>` - Delete user

## 🔧 Troubleshooting

For troubleshooting and frequently asked questions, see **SETUP_GUIDE.md** and **DATABASE_CONNECTION_GUIDE.md**.

## 📈 Future Enhancements

- [ ] Real-time notifications
- [ ] Mobile application
- [ ] Advanced authentication (OAuth, 2FA)
- [ ] Password hashing (bcrypt)
- [ ] AI-based productivity analysis
- [ ] PDF/Excel report exports
- [ ] Integration with payment gateways
- [ ] Cloud deployment support

## 📝 License

This project is open source and available under the MIT License.

## 📞 Support

For issues, questions, or suggestions:
1. Check **SETUP_GUIDE.md** for common issues
2. Read **DATABASE_CONNECTION_GUIDE.md** for database help
3. Review code comments in `app.py` and `database.py`

---

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: 2024

Happy freelancing! 🎉
