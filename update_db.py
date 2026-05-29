
import sqlite3

conn = sqlite3.connect("database.db")


conn.commit()
conn.close()

print("Done")
