import sqlite3
import json
import os

DB_PATH = "./database/database.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            Name TEXT,
            Cover TEXT,
            base TEXT,
            Tags TEXT,        -- stored as JSON
            BookMarks TEXT,   -- stored as JSON
            Highlights TEXT,  -- stored as JSON
            Chapters TEXT     -- stored as JSON
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def add_book(book):
    # book: dict with keys: id, Name, Cover, base, Tags, BookMarks, Highlights, Chapters
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books (id, Name, Cover, base, Tags, BookMarks, Highlights, Chapters)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        book["id"], 
        book["Name"], 
        book["Cover"], 
        book["base"],
        json.dumps(book.get("Tags", [])),
        json.dumps(book.get("BookMarks", [])),
        json.dumps(book.get("Highlights", [])),
        json.dumps(book.get("Chapters", []))
    ))
    conn.commit()
    conn.close()

def update_book(book):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE books 
        SET Name=?, Cover=?, base=?, Tags=?, BookMarks=?, Highlights=?, Chapters=?
        WHERE id=?
    """, (
        book["Name"],
        book["Cover"],
        book["base"],
        json.dumps(book.get("Tags", [])),
        json.dumps(book.get("BookMarks", [])),
        json.dumps(book.get("Highlights", [])),
        json.dumps(book.get("Chapters", [])),
        book["id"]
    ))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def get_book(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE id=?", (book_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        book = dict(row)
        # Decode JSON fields
        for field in ["Tags", "BookMarks", "Highlights", "Chapters"]:
            book[field] = json.loads(book[field]) if book[field] else []
        return book
    return None

def get_all_books():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    rows = cur.fetchall()
    conn.close()
    books = []
    for row in rows:
        book = dict(row)
        for field in ["Tags", "BookMarks", "Highlights", "Chapters"]:
            book[field] = json.loads(book[field]) if book[field] else []
        books.append(book)
    return books

def add_tag(tag):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO tags (tag) VALUES (?)", (tag,))
    conn.commit()
    conn.close()

def delete_tag(tag):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tags WHERE tag=?", (tag,))
    conn.commit()
    conn.close()

def get_all_tags():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tag FROM tags")
    rows = cur.fetchall()
    conn.close()
    return [row["tag"] for row in rows]