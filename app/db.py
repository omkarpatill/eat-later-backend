import sqlite3
import os

DB_NAME = 'restaurants.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                rating REAL,
                address TEXT,
                timings TEXT,
                place_id TEXT,
                location TEXT,
                food_type TEXT
            )
        ''')
