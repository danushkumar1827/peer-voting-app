import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Create a table for tokens
cur.execute("""
CREATE TABLE IF NOT EXISTS tokens (
    token TEXT PRIMARY KEY,
    participant_name TEXT,
    used INTEGER DEFAULT 0
)
""")

# Create a table for votes
cur.execute("""
CREATE TABLE IF NOT EXISTS votes (
    token TEXT PRIMARY KEY,
    Smit REAL,
    Jaheer REAL,
    Abdul REAL,
    Danush REAL,
    Nawwar REAL,
    Sara REAL,
    Avinash REAL,
    Saurab REAL
)
""")

# Insert 8 participants with unique tokens
tokens = [
    ("XJ92", "Smit"),
    ("Q4KP", "Jaheer"),
    ("Z7LT", "Abdul"),
    ("A8FR", "Danush"),
    ("M6DS", "Nawwar"),
    ("B9HK", "Sara"),
    ("C2PL", "Avinash"),
    ("F7JQ", "Saurab"),
]

cur.executemany("INSERT INTO tokens (token, participant_name) VALUES (?, ?)", tokens)

# Save changes and close the connection
conn.commit()
conn.close()

print("Database created successfully with 8 tokens!")