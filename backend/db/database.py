import os
import sqlite3
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
config = load_config()

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATABASE_PATH = os.path.join(BASE_PATH, config["database"])
BOOKS_FOLDER = os.path.join(BASE_PATH, config["books_folder"])
EPUB_FOLDER = os.path.join(BASE_PATH, config["epub_books_folder"])

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            id TEXT PRIMARY KEY,
            name TEXT,
            cover TEXT,
            base TEXT,
            chapters TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS BookMarks (
            id TEXT PRIMARY KEY,
            book_id TEXT,
            name TEXT,
            cfi TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS GlobalTags (
            tag TEXT PRIMARY KEY
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS BookTags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT,
            tag TEXT
        )
    """)
    conn.commit()
    conn.close()

def execute_query(query, params=(), commit=False, fetchone=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, params)
    result = None
    if commit:
        conn.commit()
    else:
        result = cur.fetchone() if fetchone else cur.fetchall()
    conn.close()
    return result
