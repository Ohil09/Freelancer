"""
Freelancer Time and Invoice Management System
Main Flask Application

This application provides a web-based platform for managing freelancer projects,
tracking work hours, monitoring productivity, and managing invoices.
"""

from flask import Flask, render_template, request, redirect, session, jsonify
from functools import wraps
from database import get_db_connection, init_database, close_db_connection
import os

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")

# Initialize database on startup (idempotent)
init_database()


# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to check if user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") != "admin":
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function


def freelancer_required(f):
    """Decorator to check if user is a freelancer"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        if session.get("role") != "freelancer":
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("login.html", error="Username and password required")
        
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        close_db_connection(conn)
        
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Handle user logout"""
    session.clear()
    return redirect("/login")


# ==================== DASHBOARD ROUTES ====================

@app.route("/")
@login_required
def dashboard():
    """Display dashboard based on user role"""
    if session["role"] == "admin":
        return admin_dashboard()
    else:
        return freelancer_dashboard()


def admin_dashboard():
    """Admin dashboard with system overview"""
    conn = get_db_connection()
    
    # Get all projects with hours
    projects = conn.execute("""
        SELECT 
            projects.*,
            users.username,
            IFNULL(SUM(time_logs.hours), 0) as total_hours
        FROM projects
        LEFT JOIN time_logs ON projects.id = time_logs.project_id
        LEFT JOIN users ON projects.user_id = users.id
        GROUP BY projects.id
        ORDER BY projects.created_at DESC
    """).fetchall()
    
    # Calculate stats
    total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    active_projects = conn.execute("SELECT COUNT(*) FROM projects WHERE status='Active'").fetchone()[0]
    total_hours = conn.execute("SELECT IFNULL(SUM(hours), 0) FROM time_logs").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    
    # Calculate total earnings
    total_earnings = 0
    for p in projects:
        hours = float(p["total_hours"] or 0)
        rate = float(p["rate"] or 0)
        total_earnings += hours * rate
    
    close_db_connection(conn)
    
    return render_template(
        "admin_dashboard.html",
        projects=projects,
        total_projects=total_projects,
        active_projects=active_projects,
        total_hours=total_hours,
        total_earnings=total_earnings,
        total_users=total_users
    )


def freelancer_dashboard():
    """Freelancer dashboard with personal projects"""
    user_id = session["user_id"]
    conn = get_db_connection()
    
    # Get user's projects
    projects = conn.execute("""
        SELECT 
            projects.*,
            IFNULL(SUM(time_logs.hours), 0) as total_hours
        FROM projects
        LEFT JOIN time_logs ON projects.id = time_logs.project_id
        WHERE projects.user_id = ?
        GROUP BY projects.id
        ORDER BY projects.created_at DESC
    """, (user_id,)).fetchall()
    
    # Calculate stats
    total_projects = len(projects)
    active_projects = conn.execute(
        "SELECT COUNT(*) FROM projects WHERE status='Active' AND user_id=?",
        (user_id,)
    ).fetchone()[0]
    total_hours = conn.execute(
        "SELECT IFNULL(SUM(hours), 0) FROM time_logs WHERE user_id=?",
        (user_id,)
    ).fetchone()[0]
    
    # Calculate total earnings
    total_earnings = 0
    for p in projects:
        hours = float(p["total_hours"] or 0)
        rate = float(p["rate"] or 0)
        total_earnings += hours * rate
    
    close_db_connection(conn)
    
    return render_template(
        "freelancer_dashboard.html",
        projects=projects,
        total_projects=total_projects,
        active_projects=active_projects,
        total_hours=total_hours,
        total_earnings=total_earnings
    )


# ==================== USER MANAGEMENT ROUTES ====================

@app.route("/manage_users", methods=["GET", "POST"])
@admin_required
def manage_users():
    """Manage system users (admin only)"""
    conn = get_db_connection()
    error = None
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "freelancer")
        email = request.form.get("email", "")
        
        # Validate input
        if not username or not password:
            error = "Username and password required"
        else:
            try:
                # Check if user already exists
                existing = conn.execute(
                    "SELECT * FROM users WHERE username=?",
                    (username,)
                ).fetchone()
                
                if existing:
                    error = "Username already exists"
                else:
                    # Insert new user
                    conn.execute(
                        "INSERT INTO users(username, password, role, email) VALUES (?, ?, ?, ?)",
                        (username, password, role, email)
                    )
                    conn.commit()
                    error = None
            except Exception as e:
                error = f"Error adding user: {str(e)}"
                conn.rollback()
    
    users = conn.execute("SELECT * FROM users").fetchall()
    close_db_connection(conn)
    
    return render_template("manage_users.html", users=users, error=error)


@app.route("/delete_user/<int:user_id>")
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    conn = get_db_connection()
    
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    
    # Prevent deleting admin
    if user and user["role"] == "admin":
        close_db_connection(conn)
        return "Cannot delete admin user", 403
    
    # Delete user
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    close_db_connection(conn)
    
    return redirect("/manage_users")


# ==================== PROJECT MANAGEMENT ROUTES ====================

@app.route("/projects")
@login_required
def projects():
    """View projects"""
    user_id = session["user_id"]
    role = session["role"]
    conn = get_db_connection()
    
    if role == "admin":
        projects = conn.execute("""
            SELECT 
                projects.*,
                users.username,
                IFNULL(SUM(time_logs.hours), 0) as total_hours
            FROM projects
            LEFT JOIN time_logs ON projects.id = time_logs.project_id
            LEFT JOIN users ON projects.user_id = users.id
            GROUP BY projects.id
            ORDER BY projects.created_at DESC
        """).fetchall()
    else:
        projects = conn.execute("""
            SELECT 
                projects.*,
                IFNULL(SUM(time_logs.hours), 0) as total_hours
            FROM projects
            LEFT JOIN time_logs ON projects.id = time_logs.project_id
            WHERE projects.user_id = ?
            GROUP BY projects.id
            ORDER BY projects.created_at DESC
        """, (user_id,)).fetchall()
    
    close_db_connection(conn)
    
    return render_template("projects.html", projects=projects, role=role)


@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    """Add a new project"""
    conn = get_db_connection()
    role = session["role"]
    error = None
    
    # Get users list for admin
    users = []
    if role == "admin":
        users = conn.execute("SELECT id, username FROM users WHERE role='freelancer'").fetchall()
    
    if request.method == "POST":
        name = request.form.get("name")
        project_type = request.form.get("type")
        rate = request.form.get("rate")
        status = request.form.get("status", "Active")
        deadline = request.form.get("deadline", "")
        description = request.form.get("description", "")
        
        # Validate input
        if not name or not project_type or not rate:
            close_db_connection(conn)
            return render_template(
                "add_project.html",
                users=users,
                error="Name, type, and rate are required"
            )
        
        # Determine user_id
        if role == "admin":
            user_id = request.form.get("user_id")
            if not user_id:
                close_db_connection(conn)
                return render_template(
                    "add_project.html",
                    users=users,
                    error="Please select a freelancer"
                )
        else:
            user_id = session["user_id"]
        
        # Insert project
        try:
            conn.execute(
                """INSERT INTO projects(
                        name, type, rate, status, user_id, deadline, description, created_at
                    )
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (name, project_type, rate, status, user_id, deadline, description)
            )
            conn.commit()
            close_db_connection(conn)
            return redirect("/projects")
        except Exception as e:
            error = f"Error adding project: {str(e)}"
            close_db_connection(conn)
            return render_template(
                "add_project.html",
                users=users,
                error=error
            )
    
    close_db_connection(conn)
    return render_template("add_project.html", users=users, error=error)


@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    """Edit a project"""
    conn = get_db_connection()
    user_id = session["user_id"]
    role = session["role"]
    
    # Get project
    if role == "admin":
        project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    else:
        project = conn.execute(
            "SELECT * FROM projects WHERE id=? AND user_id=?",
            (project_id, user_id)
        ).fetchone()
    
    if not project:
        close_db_connection(conn)
        return "Project not found", 404
    
    if request.method == "POST":
        name = request.form.get("name")
        project_type = request.form.get("type")
        rate = request.form.get("rate")
        status = request.form.get("status")
        deadline = request.form.get("deadline", "")
        description = request.form.get("description", "")
        
        conn.execute(
            """UPDATE projects
               SET name=?, type=?, rate=?, status=?, deadline=?, description=?
               WHERE id=?""",
            (name, project_type, rate, status, deadline, description, project_id)
        )
        conn.commit()
        close_db_connection(conn)
        
        return redirect("/projects")
    
    close_db_connection(conn)
    return render_template("edit_project.html", project=project)


@app.route("/delete_project/<int:project_id>")
@login_required
def delete_project(project_id):
    """Delete a project"""
    conn = get_db_connection()
    user_id = session["user_id"]
    role = session["role"]
    
    if role == "admin":
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    else:
        conn.execute(
            "DELETE FROM projects WHERE id=? AND user_id=?",
            (project_id, user_id)
        )
    
    conn.commit()
    close_db_connection(conn)
    
    return redirect("/projects")


# ==================== TIME TRACKING ROUTES ====================

@app.route("/time_tracking", methods=["GET", "POST"])
@login_required
def time_tracking():
    """Track working hours"""
    user_id = session["user_id"]
    role = session["role"]
    conn = get_db_connection()
    error = None
    
    if request.method == "POST":
        project_id = request.form.get("project_id")
        hours = request.form.get("hours")
        description = request.form.get("description", "")
        
        if not project_id or not hours:
            error = "Project and hours are required"
        
        if not error:
            try:
                hours = float(hours)
                if hours <= 0:
                    error = "Hours must be greater than 0"
            except ValueError:
                error = "Invalid hours value"
        
        if not error:
            conn.execute(
                """INSERT INTO time_logs(project_id, user_id, hours, description)
                   VALUES (?, ?, ?, ?)""",
                (project_id, user_id, hours, description)
            )
            conn.commit()
            close_db_connection(conn)
            return redirect("/time_tracking")
    
    # Get projects
    if role == "admin":
        projects = conn.execute("SELECT id, name FROM projects").fetchall()
        logs = conn.execute("""
            SELECT time_logs.*, projects.name as project_name, users.username
            FROM time_logs
            JOIN projects ON time_logs.project_id = projects.id
            JOIN users ON time_logs.user_id = users.id
            ORDER BY time_logs.date DESC LIMIT 50
        """).fetchall()
    else:
        projects = conn.execute(
            "SELECT id, name FROM projects WHERE user_id=?",
            (user_id,)
        ).fetchall()
        logs = conn.execute("""
            SELECT time_logs.*, projects.name as project_name
            FROM time_logs
            JOIN projects ON time_logs.project_id = projects.id
            WHERE time_logs.user_id = ?
            ORDER BY time_logs.date DESC LIMIT 50
        """, (user_id,)).fetchall()
    
    close_db_connection(conn)
    
    return render_template(
        "time_tracking.html",
        projects=projects,
        logs=logs,
        role=role,
        error=error,
        selected_project=request.form.get("project_id") if request.method == "POST" else request.args.get("project_id")
    )


@app.route("/time/<int:project_id>", methods=["GET", "POST"])
@freelancer_required
def project_timer(project_id):
    """Auto time tracking for a single project"""
    user_id = session["user_id"]
    conn = get_db_connection()
    project = conn.execute(
        "SELECT * FROM projects WHERE id=? AND user_id=?",
        (project_id, user_id)
    ).fetchone()
    
    if not project:
        close_db_connection(conn)
        return "Project not found", 404
    
    if request.method == "POST":
        hours = request.form.get("hours")
        request_invoice = request.form.get("request_invoice")
        description = request.form.get("description", "Timer entry")
        
        try:
            hours_value = float(hours or 0)
        except ValueError:
            hours_value = 0
        
        if hours_value <= 0:
            close_db_connection(conn)
            return render_template(
                "time.html",
                project=project,
                error="Please stop the timer to calculate hours before saving."
            )
        
        conn.execute(
            """INSERT INTO time_logs(project_id, user_id, hours, description)
               VALUES (?, ?, ?, ?)""",
            (project_id, user_id, hours_value, description)
        )
        conn.commit()
        close_db_connection(conn)
        
        if request_invoice == "1":
            return redirect(f"/invoice_request/{project_id}")
        
        return redirect("/")
    
    close_db_connection(conn)
    return render_template("time.html", project=project)


# ==================== PROJECT PROGRESS ROUTES ====================

@app.route("/project_progress", methods=["GET", "POST"])
@login_required
def project_progress():
    """Track project progress"""
    user_id = session["user_id"]
    conn = get_db_connection()
    
    if request.method == "POST":
        project_id = request.form.get("project_id")
        progress = request.form.get("progress", 0)
        completed_tasks = request.form.get("completed_tasks")
        remaining_work = request.form.get("remaining_work")
        remarks = request.form.get("remarks", "")
        
        try:
            progress = int(progress)
            if not (0 <= progress <= 100):
                raise ValueError("Progress must be between 0 and 100")
        except ValueError:
            return render_template(
                "project_progress.html",
                error="Invalid progress value"
            )
        
        conn.execute(
            """INSERT INTO progress_updates
               (project_id, user_id, progress, completed_tasks, remaining_work, remarks)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (project_id, user_id, progress, completed_tasks, remaining_work, remarks)
        )
        conn.commit()
    
    # Get user's projects
    projects = conn.execute(
        "SELECT id, name FROM projects WHERE user_id=? ORDER BY name",
        (user_id,)
    ).fetchall()
    
    # Get progress updates
    updates = conn.execute("""
        SELECT progress_updates.*, projects.name as project_name
        FROM progress_updates
        JOIN projects ON progress_updates.project_id = projects.id
        WHERE progress_updates.user_id = ?
        ORDER BY progress_updates.update_date DESC
    """, (user_id,)).fetchall()
    
    close_db_connection(conn)
    
    return render_template(
        "project_progress.html",
        projects=projects,
        updates=updates
    )


# ==================== INVOICE MANAGEMENT ROUTES ====================

@app.route("/invoice/<int:project_id>")
@login_required
def invoice(project_id):
    """Generate invoice for a project.

    Admins may view any project's invoice. Freelancers may only view invoices
    for projects they own.
    """
    role = session.get("role")
    user_id = session.get("user_id")
    conn = get_db_connection()

    # Get project: admins can view any project, freelancers only their own
    if role == "admin":
        project = conn.execute(
            "SELECT * FROM projects WHERE id=?",
            (project_id,)
        ).fetchone()
        invoice_hours_row = conn.execute(
            "SELECT IFNULL(SUM(hours), 0) as total FROM time_logs WHERE project_id=?",
            (project_id,)
        ).fetchone()
    else:
        project = conn.execute(
            "SELECT * FROM projects WHERE id=? AND user_id=?",
            (project_id, user_id)
        ).fetchone()
        invoice_hours_row = conn.execute(
            "SELECT IFNULL(SUM(hours), 0) as total FROM time_logs WHERE project_id=? AND user_id=?",
            (project_id, user_id)
        ).fetchone()

    if not project:
        close_db_connection(conn)
        return "Project not found", 404

    total_hours = float(invoice_hours_row["total"] or 0)
    total_amount = total_hours * float(project["rate"])

    close_db_connection(conn)

    return render_template(
        "invoice.html",
        project=project,
        hours=total_hours,
        total=total_amount
    )


@app.route("/invoice_request/<int:project_id>", methods=["GET", "POST"])
@freelancer_required
def invoice_request(project_id):
    """Request invoice approval"""
    user_id = session["user_id"]
    conn = get_db_connection()
    
    # Get project
    project = conn.execute(
        "SELECT * FROM projects WHERE id=? AND user_id=?",
        (project_id, user_id)
    ).fetchone()
    
    if not project:
        close_db_connection(conn)
        return "Project not found", 404
    
    total_hours_result = conn.execute(
        "SELECT IFNULL(SUM(hours), 0) as total FROM time_logs WHERE project_id=? AND user_id=?",
        (project_id, user_id)
    ).fetchone()
    
    total_hours = float(total_hours_result["total"] or 0)
    total_amount = total_hours * float(project["rate"])
    
    if request.method == "POST":
        # Allow client to include an active running session's hours
        running_hours = request.form.get('running_hours')
        try:
            running_hours_val = float(running_hours) if running_hours else 0.0
        except ValueError:
            running_hours_val = 0.0

        final_hours = total_hours + running_hours_val
        final_amount = final_hours * float(project['rate'])

        # Create invoice request
        conn.execute(
            """INSERT INTO invoice_requests
               (project_id, user_id, total_hours, total_amount)
               VALUES (?, ?, ?, ?)""",
            (project_id, user_id, final_hours, final_amount)
        )
        conn.commit()
        close_db_connection(conn)
        
        return redirect("/invoices")
    
    close_db_connection(conn)
    return render_template(
        "invoice_request.html",
        project=project,
        hours=total_hours,
        total=total_amount
    )


@app.route("/invoices")
@login_required
def invoices():
    """View invoices"""
    user_id = session["user_id"]
    role = session["role"]
    conn = get_db_connection()
    
    if role == "admin":
        invoices = conn.execute("""
            SELECT invoice_requests.*, projects.name as project_name, users.username
            FROM invoice_requests
            JOIN projects ON invoice_requests.project_id = projects.id
            JOIN users ON invoice_requests.user_id = users.id
            ORDER BY invoice_requests.requested_date DESC
        """).fetchall()
    else:
        invoices = conn.execute("""
            SELECT invoice_requests.*, projects.name as project_name
            FROM invoice_requests
            JOIN projects ON invoice_requests.project_id = projects.id
            WHERE invoice_requests.user_id = ?
            ORDER BY invoice_requests.requested_date DESC
        """, (user_id,)).fetchall()
    
    close_db_connection(conn)
    
    return render_template("invoices.html", invoices=invoices, role=role)


@app.route("/approve_invoice/<int:invoice_id>")
@login_required
def approve_invoice(invoice_id):
    """Approve invoice (admin or invoice owner)"""
    user_id = session.get("user_id")
    role = session.get("role")
    conn = get_db_connection()

    invoice = conn.execute(
        "SELECT * FROM invoice_requests WHERE id=?",
        (invoice_id,)
    ).fetchone()

    if invoice:
        # Only admin or the invoice owner can approve
        if role != "admin" and invoice["user_id"] != user_id:
            close_db_connection(conn)
            return "Access Denied", 403

        # Update invoice status
        conn.execute(
            "UPDATE invoice_requests SET status='Approved' WHERE id=?",
            (invoice_id,)
        )

        # Create payment record
        conn.execute(
            """INSERT INTO payments(invoice_id, project_id, user_id, amount, payment_status)
               VALUES (?, ?, ?, ?, 'Pending')""",
            (invoice_id, invoice["project_id"], invoice["user_id"], invoice["total_amount"])
        )

        conn.commit()

    close_db_connection(conn)
    return redirect("/invoices")


@app.route("/reject_invoice/<int:invoice_id>")
@login_required
def reject_invoice(invoice_id):
    """Reject invoice (admin or invoice owner)"""
    user_id = session.get("user_id")
    role = session.get("role")
    conn = get_db_connection()

    invoice = conn.execute(
        "SELECT * FROM invoice_requests WHERE id=?",
        (invoice_id,)
    ).fetchone()

    if not invoice:
        close_db_connection(conn)
        return "Invoice not found", 404

    if role != "admin" and invoice["user_id"] != user_id:
        close_db_connection(conn)
        return "Access Denied", 403

    conn.execute(
        "UPDATE invoice_requests SET status='Rejected' WHERE id=?",
        (invoice_id,)
    )
    conn.commit()
    close_db_connection(conn)

    return redirect("/invoices")


# ==================== PAYMENT MANAGEMENT ROUTES ====================

@app.route("/payments")
@login_required
def payments():
    """View payment records. Admin sees all; users see their own payments."""
    user_id = session.get("user_id")
    role = session.get("role")
    conn = get_db_connection()

    if role == "admin":
        payments = conn.execute("""
            SELECT payments.*, users.username, projects.name as project_name
            FROM payments
            JOIN users ON payments.user_id = users.id
            JOIN projects ON payments.project_id = projects.id
            ORDER BY payments.created_at DESC
        """).fetchall()
    else:
        payments = conn.execute("""
            SELECT payments.*, users.username, projects.name as project_name
            FROM payments
            JOIN users ON payments.user_id = users.id
            JOIN projects ON payments.project_id = projects.id
            WHERE payments.user_id = ?
            ORDER BY payments.created_at DESC
        """, (user_id,)).fetchall()

    close_db_connection(conn)

    return render_template("payments.html", payments=payments)


@app.route("/update_payment_status/<int:payment_id>/<status>")
@login_required
def update_payment_status(payment_id, status):
    """Update payment status. Admin can update any; users can update their own payments."""
    if status not in ["Pending", "Completed", "Failed"]:
        return "Invalid status", 400

    user_id = session.get("user_id")
    role = session.get("role")

    conn = get_db_connection()
    payment = conn.execute("SELECT * FROM payments WHERE id=?", (payment_id,)).fetchone()

    if not payment:
        close_db_connection(conn)
        return "Payment not found", 404

    # Only admin or the payment owner can update status
    if role != "admin" and payment["user_id"] != user_id:
        close_db_connection(conn)
        return "Access Denied", 403

    if status == "Completed":
        conn.execute(
            "UPDATE payments SET payment_status=?, payment_date=CURRENT_TIMESTAMP WHERE id=?",
            (status, payment_id)
        )
    else:
        conn.execute(
            "UPDATE payments SET payment_status=? WHERE id=?",
            (status, payment_id)
        )

    conn.commit()
    close_db_connection(conn)

    return redirect("/payments")


# ==================== ADMIN MONITORING ROUTES ====================

@app.route("/admin/users")
@admin_required
def admin_users():
    """Shortcut to manage users"""
    return redirect("/manage_users")

@app.route("/admin/progress")
@admin_required
def admin_progress():
    """View progress updates"""
    conn = get_db_connection()
    
    updates = conn.execute("""
        SELECT progress_updates.*, projects.name as project_name, users.username
        FROM progress_updates
        JOIN projects ON progress_updates.project_id = projects.id
        JOIN users ON progress_updates.user_id = users.id
        ORDER BY progress_updates.update_date DESC
    """).fetchall()
    
    close_db_connection(conn)
    
    return render_template("admin_progress.html", updates=updates)

@app.route("/admin/project_monitor")
@admin_required
def admin_project_monitor():
    """Monitor project progress updates"""
    conn = get_db_connection()
    
    updates = conn.execute("""
        SELECT progress_updates.*, projects.name as project_name, users.username
        FROM progress_updates
        JOIN projects ON progress_updates.project_id = projects.id
        JOIN users ON progress_updates.user_id = users.id
        ORDER BY progress_updates.update_date DESC
    """).fetchall()
    
    close_db_connection(conn)
    
    return render_template("admin_project_monitor.html", updates=updates)

@app.route("/admin/activity")
@admin_required
def admin_activity():
    """Monitor freelancer activity"""
    conn = get_db_connection()
    
    # Get all time logs with user and project info
    logs = conn.execute("""
        SELECT time_logs.*, projects.name as project_name, users.username
        FROM time_logs
        JOIN projects ON time_logs.project_id = projects.id
        JOIN users ON time_logs.user_id = users.id
        ORDER BY time_logs.date DESC LIMIT 100
    """).fetchall()
    
    close_db_connection(conn)
    
    return render_template("admin_activity.html", logs=logs)


@app.route("/admin/productivity")
@admin_required
def admin_productivity():
    """View productivity reports"""
    conn = get_db_connection()
    
    # Get productivity by user
    users_productivity = conn.execute("""
        SELECT 
            users.id,
            users.username,
            COUNT(DISTINCT projects.id) as project_count,
            IFNULL(SUM(time_logs.hours), 0) as total_hours
        FROM users
        LEFT JOIN projects ON users.id = projects.user_id
        LEFT JOIN time_logs ON users.id = time_logs.user_id
        WHERE users.role = 'freelancer'
        GROUP BY users.id
        ORDER BY total_hours DESC
    """).fetchall()
    
    close_db_connection(conn)
    
    return render_template("admin_productivity.html", users=users_productivity)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("error.html", message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template("error.html", message="Internal server error"), 500


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Run Flask app
    # For development, set FLASK_DEBUG=True environment variable
    # For production, ensure FLASK_DEBUG is not set or False
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
