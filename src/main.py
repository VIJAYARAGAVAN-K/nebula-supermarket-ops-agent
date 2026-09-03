import sqlite3

DB = "database/supermarket.db"

with open("database/schema.sql", "r") as file:
    schema = file.read()

conn = sqlite3.connect(DB)
conn.executescript(schema)
conn.close()

print("Database initialized successfully!")