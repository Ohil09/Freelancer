from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB =================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # USERS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS project_updates(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     project_id INTEGER,
     user_id INTEGER,
     completed_tasks TEXT,
     pending_tasks TEXT,
     progress INTEGER,
     remarks TEXT,
     update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    # PROJECTS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        rate INTEGER,
        status TEXT,
        user_id INTEGER
    )
    """)

    # TIME LOGS TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS time_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        hours REAL,
        user_id INTEGER
    )
    """)

    # PROGRESS UPDATES TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS progress_updates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    user_id INTEGER,
    progress INTEGER,
    completed_tasks TEXT,
    remaining_work TEXT,
    remarks TEXT,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
        # INVOICE REQUESTS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS invoice_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        user_id INTEGER,
        status TEXT DEFAULT 'Pending'
    )
    """)
        #PAYMENTS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        user_id INTEGER,
        amount REAL,
        payment_status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute("""
            SELECT * FROM users
            WHERE username=? AND password=?
        """, (username, password)).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

        else:
            return "Invalid login"

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ================= DASHBOARD =================
@app.route("/")
def dashboard():

    # LOGIN CHECK
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    # ================= ADMIN DASHBOARD =================
    if session["role"] == "admin":

        projects = conn.execute("""
            SELECT 
                projects.*,
                IFNULL(SUM(time_logs.hours),0) as total_hours
            FROM projects

            LEFT JOIN time_logs
            ON projects.id = time_logs.project_id

            GROUP BY projects.id
        """).fetchall()

        total_projects = conn.execute("""
            SELECT COUNT(*) FROM projects
        """).fetchone()[0]

        active_projects = conn.execute("""
            SELECT COUNT(*)
            FROM projects
            WHERE status='Active'
        """).fetchone()[0]

        total_hours = conn.execute("""
            SELECT IFNULL(SUM(hours),0)
            FROM time_logs
        """).fetchone()[0]

        total_users = conn.execute("""
            SELECT COUNT(*) FROM users
        """).fetchone()[0]

        total_earnings = 0

        for p in projects:

            hours = float(p["total_hours"] or 0)
            rate = float(p["rate"] or 0)

            total_earnings += hours * rate

        conn.close()

        return render_template(
            "admin_dashboard.html",
            projects=projects,
            total_projects=total_projects,
            active_projects=active_projects,
            total_hours=total_hours,
            total_earnings=total_earnings,
            total_users=total_users
        )

    # ================= FREELANCER DASHBOARD =================
    projects = conn.execute("""
        SELECT 
            projects.*,
            IFNULL(SUM(time_logs.hours),0) as total_hours
        FROM projects

        LEFT JOIN time_logs
        ON projects.id = time_logs.project_id

        WHERE projects.user_id=?

        GROUP BY projects.id
    """, (session["user_id"],)).fetchall()

    total_projects = len(projects)

    active_projects = conn.execute("""
        SELECT COUNT(*)
        FROM projects
        WHERE status='Active'
        AND user_id=?
    """, (session["user_id"],)).fetchone()[0]

    total_hours = conn.execute("""
        SELECT IFNULL(SUM(hours),0)
        FROM time_logs
        WHERE user_id=?
    """, (session["user_id"],)).fetchone()[0]

    total_earnings = 0

    for p in projects:

        hours = float(p["total_hours"] or 0)
        rate = float(p["rate"] or 0)

        total_earnings += hours * rate

    conn.close()

    return render_template(
        "freelancer_dashboard.html",
        projects=projects,
        total_projects=total_projects,
        active_projects=active_projects,
        total_hours=total_hours,
        total_earnings=total_earnings
    )
# ================= MANAGE USERS =================
@app.route("/manage_users", methods=["GET", "POST"])
def manage_users():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    conn = get_db()

    # ADD USER
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        existing = conn.execute("""
            SELECT * FROM users
            WHERE username=?
        """, (username,)).fetchone()

        if existing:
            conn.close()
            return "Username already exists"

        conn.execute("""
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, role))

        conn.commit()

    users = conn.execute("""
        SELECT * FROM users
    """).fetchall()

    conn.close()

    return render_template(
        "manage_users.html",
        users=users
    )


# ================= DELETE USER =================
@app.route("/delete_user/<int:id>")
def delete_user(id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    conn = get_db()

    user = conn.execute("""
        SELECT * FROM users
        WHERE id=?
    """, (id,)).fetchone()

    # Prevent deleting admin
    if user and user["role"] == "admin":
        conn.close()
        return "Cannot delete admin"

    conn.execute("""
        DELETE FROM users
        WHERE id=?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/manage_users")


# ================= PROJECTS =================
@app.route("/projects")
def projects():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if session["role"] == "admin":

        projects = conn.execute("""
            SELECT 
                projects.*,
                IFNULL(SUM(time_logs.hours),0) AS total_hours

            FROM projects

            LEFT JOIN time_logs
            ON projects.id = time_logs.project_id

            GROUP BY projects.id
        """).fetchall()

    else:

        projects = conn.execute("""
            SELECT 
                projects.*,
                IFNULL(SUM(time_logs.hours),0) AS total_hours

            FROM projects

            LEFT JOIN time_logs
            ON projects.id = time_logs.project_id

            WHERE projects.user_id=?

            GROUP BY projects.id
        """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "projects.html",
        projects=projects
    )


# ================= ADD PROJECT =================
@app.route("/add_project", methods=["GET", "POST"])
def add_project():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    users = conn.execute("""
        SELECT * FROM users
    """).fetchall()

    if request.method == "POST":

        name = request.form["name"]
        type = request.form["type"]
        rate = request.form["rate"]
        status = request.form["status"]

        if session["role"] == "admin":
            user_id = request.form["user_id"]
        else:
            user_id = session["user_id"]

        conn.execute("""
            INSERT INTO projects(name, type, rate, status, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, type, rate, status, user_id))

        conn.commit()
        conn.close()

        return redirect("/projects")

    return render_template(
        "add_project.html",
        users=users
    )


# ================= EDIT PROJECT =================
@app.route("/edit_project/<int:id>", methods=["GET", "POST"])
def edit_project(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if session["role"] == "admin":

        project = conn.execute("""
            SELECT * FROM projects
            WHERE id=?
        """, (id,)).fetchone()

    else:

        project = conn.execute("""
            SELECT * FROM projects
            WHERE id=? AND user_id=?
        """, (id, session["user_id"])).fetchone()

    if not project:
        conn.close()
        return "Project not found"

    if request.method == "POST":

        name = request.form["name"]
        type = request.form["type"]
        rate = request.form["rate"]
        status = request.form["status"]

        conn.execute("""
            UPDATE projects
            SET name=?, type=?, rate=?, status=?
            WHERE id=?
        """, (
            name,
            type,
            rate,
            status,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/projects")

    conn.close()

    return render_template(
        "edit_project.html",
        project=project
    )


# ================= DELETE PROJECT =================
@app.route("/delete_project/<int:id>")
def delete_project(id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if session["role"] == "admin":

        conn.execute("""
            DELETE FROM projects
            WHERE id=?
        """, (id,))

    else:

        conn.execute("""
            DELETE FROM projects
            WHERE id=? AND user_id=?
        """, (id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/projects")

# ================= TIME TRACKING =================
@app.route('/time_tracking', methods=['GET', 'POST'])
def time_tracking():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Save time entry
    if request.method == 'POST':
        project_id = request.form['project_id']
        hours = request.form['hours']

        cursor.execute("""
            INSERT INTO time_logs (project_id, hours)
            VALUES (?, ?)
        """, (project_id, hours))

        conn.commit()
        return redirect('/time_tracking')

    # Fetch all projects for admin dropdown
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    # Fetch recent logs
    cursor.execute("""
        SELECT time_logs.hours, projects.name
        FROM time_logs
        JOIN projects ON time_logs.project_id = projects.id
        ORDER BY time_logs.id DESC
    """)

    recent = cursor.fetchall()

    conn.close()

    return render_template(
        'time_tracking.html',
        projects=projects,
        recent=recent
    )
# ================= PROJECT UPDATES =================
@app.route("/project_updates", methods=["GET", "POST"])
def project_updates():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":

        project_id = request.form["project_id"]
        completed_tasks = request.form["completed_tasks"]
        pending_tasks = request.form["pending_tasks"]
        progress = request.form["progress"]
        remarks = request.form["remarks"]

        conn.execute("""
            INSERT INTO project_updates(
                project_id,
                user_id,
                completed_tasks,
                pending_tasks,
                progress,
                remarks
            )
            VALUES(?,?,?,?,?,?)
        """, (
            project_id,
            session["user_id"],
            completed_tasks,
            pending_tasks,
            progress,
            remarks
        ))

        conn.commit()

    projects = conn.execute(
        "SELECT * FROM projects WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    updates = conn.execute("""
        SELECT project_updates.*, projects.name
        FROM project_updates
        JOIN projects
        ON projects.id = project_updates.project_id
        WHERE project_updates.user_id=?
        ORDER BY project_updates.id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "project_updates.html",
        projects=projects,
        updates=updates
    )

# ================= ADMIN PANEL =================
@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    conn = get_db()

    users = conn.execute("""
        SELECT 
            users.*,
            COUNT(DISTINCT projects.id) as project_count,
            IFNULL(SUM(time_logs.hours),0) as total_hours

        FROM users

        LEFT JOIN projects
        ON users.id = projects.user_id

        LEFT JOIN time_logs
        ON users.id = time_logs.user_id

        GROUP BY users.id
    """).fetchall()

    total_projects = conn.execute("""
        SELECT COUNT(*) FROM projects
    """).fetchone()[0]

    total_hours = conn.execute("""
        SELECT IFNULL(SUM(hours),0)
        FROM time_logs
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        total_projects=total_projects,
        total_hours=total_hours
    )

# ================= ADMIN PROGRESS =================
@app.route("/admin/progress")
def admin_progress():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    conn = get_db()

    updates = conn.execute("""
        SELECT 
            progress_updates.*,
            users.username,
            projects.name as project_name

        FROM progress_updates

        JOIN users
        ON users.id = progress_updates.user_id

        JOIN projects
        ON projects.id = progress_updates.project_id

        ORDER BY progress_updates.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_progress.html",
        updates=updates
    )
# ================= INVOICE =================
@app.route("/invoice/<int:project_id>")
def invoice(project_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    project = conn.execute("""
        SELECT * FROM projects
        WHERE id=? AND user_id=?
    """, (project_id, session["user_id"])).fetchone()

    total_hours = conn.execute("""
        SELECT IFNULL(SUM(hours),0) as total
        FROM time_logs
        WHERE project_id=? AND user_id=?
    """, (project_id, session["user_id"])).fetchone()

    conn.close()

    if not project:
        return "Project not found"

    hours = total_hours["total"]
    total = hours * project["rate"]

    return render_template(
        "invoice.html",
        project=project,
        hours=hours,
        total=total
    )

# ================= ADMIN PROJECT MONITOR =================
@app.route("/admin/project_monitor")
def admin_project_monitor():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return "Access Denied"

    conn = get_db()

    updates = conn.execute("""
        SELECT
            progress_updates.*,
            projects.name as project_name,
            users.username

        FROM progress_updates

        JOIN projects
        ON projects.id = progress_updates.project_id

        JOIN users
        ON users.id = progress_updates.user_id

        ORDER BY progress_updates.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_project_monitor.html",
        updates=updates
    )

# ================= PROJECT PROGRESS =================
@app.route("/project_progress", methods=["GET", "POST"])
def project_progress():

    # LOGIN CHECK
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    # CREATE TABLE IF NOT EXISTS
    conn.execute("""
    CREATE TABLE IF NOT EXISTS progress_updates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        progress INTEGER,
        completed_tasks TEXT,
        remaining_work TEXT,
        remarks TEXT,
        user_id INTEGER
    )
    """)

    # SAVE FORM DATA
    if request.method == "POST":

        project_id = request.form["project_id"]
        progress = request.form["progress"]
        completed_tasks = request.form["completed_tasks"]
        remaining_work = request.form["remaining_work"]
        remarks = request.form["remarks"]

        conn.execute("""
            INSERT INTO progress_updates(
                project_id,
                progress,
                completed_tasks,
                remaining_work,
                remarks,
                user_id
            )
            VALUES(?,?,?,?,?,?)
        """, (
            project_id,
            progress,
            completed_tasks,
            remaining_work,
            remarks,
            session["user_id"]
        ))

        conn.commit()

    # GET USER PROJECTS
    projects = conn.execute("""
        SELECT * FROM projects
        WHERE user_id=?
    """, (session["user_id"],)).fetchall()

    # GET ALL UPDATES
    updates = conn.execute("""
        SELECT 
            progress_updates.*,
            projects.name as project_name

        FROM progress_updates

        JOIN projects
        ON progress_updates.project_id = projects.id

        WHERE progress_updates.user_id=?

        ORDER BY progress_updates.id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "project_progress.html",
        projects=projects,
        updates=updates
    )
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
