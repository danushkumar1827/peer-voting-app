import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Delete all votes
cur.execute("DELETE FROM votes")
conn.commit()
conn.close()

print("All votes have been erased!")