import os
import json
import base64
import secrets
import shutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from db.database import init_db, execute_query, BOOKS_FOLDER, EPUB_FOLDER

init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

def safe_path(directory, filename):
    sp = os.path.abspath(os.path.join(directory, filename))
    if not sp.startswith(os.path.abspath(directory)):
        raise HTTPException(status_code=404, detail="File not found")
    return sp

# -------------------
# BOOK-RELATED ROUTES
# -------------------

@app.get("/books/{book_id}")
def get_book(book_id: str):
    row = execute_query("SELECT * FROM Books WHERE id = ?", (book_id,), fetchone=True)
    if not row:
        raise HTTPException(status_code=404, detail="Book not found")
    book = dict(row)
    if book.get("chapters"):
        book["chapters"] = json.loads(book["chapters"])
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    mainDes = os.path.abspath(BOOKS_FOLDER)
    epubFolderDes = os.path.abspath(EPUB_FOLDER)
    from func import delBook
    delBook(book_id, mainDes, epubFolderDes)
    execute_query("DELETE FROM Books WHERE id = ?", (book_id,), commit=True)
    execute_query("DELETE FROM BookMarks WHERE book_id = ?", (book_id,), commit=True)
    execute_query("DELETE FROM BookTags WHERE book_id = ?", (book_id,), commit=True)
    return {"res": "Book deleted successfully"}

@app.get("/books/{book_id}/cover")
def get_cover(book_id: str):
    row = execute_query("SELECT cover FROM Books WHERE id = ?", (book_id,), fetchone=True)
    if not row or row["cover"] == "NotFound":
        raise HTTPException(status_code=404, detail="Cover not found")
    cover_path = row["cover"]
    if os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return {"img": encoded}
        except Exception:
            raise HTTPException(status_code=500, detail="Error reading cover image")
    raise HTTPException(status_code=404, detail="Cover not found")

@app.get("/books/{book_id}/bookmarks")
def get_bookmarks(book_id: str):
    rows = execute_query("SELECT * FROM BookMarks WHERE book_id = ?", (book_id,))
    marks = [dict(row) for row in rows]
    return {"BookMarks": marks}

@app.post("/books/{book_id}/bookmarks")
def add_bookmark(book_id: str, bookmark: dict):
    mark_id = secrets.token_hex(4)
    name = bookmark.get("name")
    cfi = bookmark.get("cfiValue")
    if not name or not cfi:
        raise HTTPException(status_code=400, detail="Invalid bookmark data")
    execute_query("INSERT INTO BookMarks (id, book_id, name, cfi) VALUES (?, ?, ?, ?)",
                  (mark_id, book_id, name, cfi), commit=True)
    return {"res": "Bookmark added successfully", "bookmark_id": mark_id}

@app.delete("/books/{book_id}/bookmarks")
def delete_bookmark(book_id: str, mark_id: str):
    execute_query("DELETE FROM BookMarks WHERE id = ? AND book_id = ?", (mark_id, book_id), commit=True)
    return {"res": "Bookmark deleted successfully"}

@app.get("/read/{book_id}")
def read_book(book_id: str):
    epubFolderDes = os.path.abspath(EPUB_FOLDER)
    return {"url": f"http://localhost:3002/epubBooks/{book_id}.epub"}

@app.get("/epubBooks/{filename}")
def serve_epub_books(filename: str):
    epubFolderDes = os.path.abspath(EPUB_FOLDER)
    safe_file = safe_path(epubFolderDes, filename)
    if not os.path.exists(safe_file):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(safe_file)

# -------------------
# TAG-RELATED ROUTES
# -------------------

@app.get("/tags")
def get_tags():
    rows = execute_query("SELECT tag FROM GlobalTags")
    tags = [row["tag"] for row in rows]
    return {"Tags": tags}

@app.post("/tags")
def add_tag(tag: str):
    if not tag:
        raise HTTPException(status_code=400, detail="Invalid tag")
    try:
        execute_query("INSERT INTO GlobalTags (tag) VALUES (?)", (tag,), commit=True)
    except Exception:
        return {"res": "Tag already exists"}
    return {"res": "Tag added successfully"}

@app.delete("/tags")
def delete_tag(tag: str):
    execute_query("DELETE FROM GlobalTags WHERE tag = ?", (tag,), commit=True)
    execute_query("DELETE FROM BookTags WHERE tag = ?", (tag,), commit=True)
    return {"res": "Tag deleted successfully"}

# -------------------
# MISC & ROOT ROUTE
# -------------------

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=3002, log_level="info", reload=True)