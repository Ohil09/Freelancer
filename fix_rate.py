import sqlite3

conn = sqlite3.connect("database.db")

# SHOW PROJECTS
projects = conn.execute("""
SELECT id, name, type, rate
FROM projects
""").fetchall()

print("\nALL PROJECTS:\n")

for p in projects:
    print(p)

print("\n")

project_id = int(input("Enter Project ID to fix: "))
correct_rate = int(input("Enter Correct Numeric Rate: "))

conn.execute("""
UPDATE projects
SET rate=?
WHERE id=?
""", (correct_rate, project_id))

conn.commit()

print("\nRate updated successfully!")

conn.close()
