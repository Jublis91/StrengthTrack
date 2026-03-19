import sqlite3
from pathlib import Path

DB_PATH = Path("data/strengthtrack.db")


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        height_cm REAL NOT NULL,
        start_weight REAL NOT NULL,
        goal TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weight_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        entry_date TEXT NOT NULL,
        weight REAL NOT NULL,
        note TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fitness_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        entry_date TEXT NOT NULL,
        test_name TEXT NOT NULL,
        result_value REAL NOT NULL,
        unit TEXT,
        note TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


def save_user(name, height_cm, start_weight, goal):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (name, height_cm, start_weight, goal)
    VALUES (?, ?, ?, ?)
    """, (name, height_cm, start_weight, goal))

    conn.commit()
    conn.close()


def get_user_profile():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, height_cm, start_weight, goal
    FROM users
    ORDER BY id ASC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row


def save_weight_entry(user_id, entry_date, weight, note):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO weight_entries (user_id, entry_date, weight, note)
    VALUES (?, ?, ?, ?)
    """, (user_id, entry_date, weight, note))

    conn.commit()
    conn.close()


def get_weight_entries(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, entry_date, weight, note
    FROM weight_entries
    WHERE user_id = ?
    ORDER BY entry_date DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def delete_weight_entry(entry_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM weight_entries
    WHERE id = ?
    """, (entry_id,))

    conn.commit()
    conn.close()

def update_weight_entry(entry_id, entry_date, weight, note):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE weight_entries
    SET entry_date = ?, weight = ?, note = ?
    WHERE id = ?
    """, (entry_date, weight, note, entry_id))

    conn.commit()
    conn.close()

def save_test_entry(user_id, entry_date, test_name, result_value, unit, note):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO fitness_tests (user_id, entry_date, test_name, result_value, unit, note)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, entry_date, test_name, result_value, unit, note))

    conn.commit()
    conn.close()

def get_test_entries(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, entry_date, test_name, result_value, unit, note
    FROM fitness_tests
    WHERE user_id = ?
    ORDER BY entry_date DESC, id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows
