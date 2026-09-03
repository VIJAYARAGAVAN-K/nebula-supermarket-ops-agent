import sqlite3

DB_NAME = "database/supermarket.db"

def get_connection():
    return sqlite3.connect(DB_NAME)
