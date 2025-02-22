from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
from addFolder import AddFolder
from addBook import AddBook
from func import intalise, delBook, generate_unique_id
from pydantic import BaseModel
import db

app = FastAPI()

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

mainDes = os.path.abspath("books")
epubFolderDes = os.path.abspath("epubBooks")
intalise()
db.init_db()

def safe_path(directory, filename):
    abs_path = os.path.abspath(os.path.join(directory, filename))
    if not abs_path.startswith(os.path.abspath(directory)):
        raise HTTPException(status_code=404, detail="File not found")
    return abs_path

class AddBookRequest(BaseModel):
    path: str

@app.get("/delBook")
async def del_book(id: str):
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    try:
        db.delete_book(id)
        delBook(id, mainDes, epubFolderDes)
        return {"res": "Book deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Error deleting book")

@app.get("/getBookMarks")
async def get_book_marks(id: str):
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"BookMarks": book.get("BookMarks", [])}

@app.post("/delBookMark")
async def del_book_bookmark(req_data: dict):
    id = req_data.get("id")
    bookmark_id = req_data.get("mark")
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    bookmarks = book.get("BookMarks", [])
    new_bookmarks = [bm for bm in bookmarks if bm.get("id") != bookmark_id]
    if len(bookmarks) == len(new_bookmarks):
        raise HTTPException(status_code=404, detail="Bookmark not found")
    book["BookMarks"] = new_bookmarks
    try:
        db.update_book(book)
        return {"res": "Bookmark deleted successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating bookmark")

@app.post("/addBookMark")
async def add_book_bookmark(req_data: dict):
    id = req_data.get("id")
    name = req_data.get("name")
    cfiValue = req_data.get("cfiValue")
    
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    bookmark_id = generate_unique_id(8)
    newbookmark = {'id': bookmark_id, 'name': name, 'cfiValue': cfiValue}
    book.setdefault("BookMarks", []).append(newbookmark)
    try:
        db.update_book(book)
        return {"res": "Bookmark added successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating bookmark")

@app.post("/delBookTag")
async def del_book_tag(req_data: dict):
    id = req_data.get("id")
    tag = req_data.get("Tag")
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if tag not in book.get("Tags", []):
        raise HTTPException(status_code=404, detail="Tag not found in book")
    book["Tags"].remove(tag)
    try:
        db.update_book(book)
        return {"res": "Tag deleted successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating book tag")

@app.post("/addBookTag")
async def add_book_tag(req_data: dict):
    id = req_data.get("id")
    tag = req_data.get("Tag")
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if tag in book.get("Tags", []):
        raise HTTPException(status_code=400, detail="Tag already exists")
    book.setdefault("Tags", []).append(tag)
    try:
        db.update_book(book)
        return {"res": "Tag added successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Error updating book tag")

# New endpoint to retrieve tags associated with a specific book
@app.get("/getBookTags")
async def get_book_tags(id: str):
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"Tags": book.get("Tags", [])}

@app.get("/delTag")
async def del_tag(tagName: str):
    try:
        # Delete tag from the global tags table.
        db.delete_tag(tagName)
        # Remove the tag from all books that have it.
        books = db.get_all_books()
        for book in books:
            tags = book.get("Tags", [])
            if tagName in tags:
                tags.remove(tagName)
                book["Tags"] = tags
                db.update_book(book)
        return {"res": "Tag deleted successfully from global tags and books"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/addTag")
async def add_tag(tagName: str):
    try:
        db.add_tag(tagName)
        return {"res": "Tag added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getTags")
async def get_main_tags():
    tags = db.get_all_tags()
    return {"Tags": tags}

@app.get("/Read")
async def read(id: str):
    book = db.get_book(id)
    if book:
        return {"url": f"http://localhost:3002/epubBooks/{book['id']}.epub"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/getBook")
async def getbook(id: str):
    book = db.get_book(id)
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/getCover")
async def get_cover(id: str):
    book = db.get_book(id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    cover_path = book.get("Cover")
    if cover_path == 'NotFound':
        return {"img": "NotFound"}
    if cover_path and os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as cover_file:
                bitmap = cover_file.read()
                img_base64 = base64.b64encode(bitmap).decode("utf-8")
                return {"img": img_base64}
        except Exception:
            raise HTTPException(status_code=500, detail="Error reading cover image")
    raise HTTPException(status_code=404, detail="Cover not found")

@app.get("/home")
async def home(tag: str = None):
    books = db.get_all_books()
    if tag:
        books = [book for book in books if tag in book.get("Tags", [])]
    # Return an empty list if no books match the filter instead of raising an error.
    return {"info": books}

@app.get("/addFolder")
async def add_folder(path: str):
    path = path.replace('"', "")
    AddFolder(path, mainDes, epubFolderDes)
    return {"res": "Folder processed", "path": path}

@app.post("/addBook")
async def add_book(data: dict):
    file = data.get("pm")
    print(file)
    AddBook(file, mainDes, epubFolderDes)
    return {"file": file}

@app.get("/")
async def hello_world():
    return {"message": "Hello, World!"}

@app.get("/epubBooks/{filename}")
async def serve_epub_books(filename: str):
    try:
        safe_file_path = safe_path(epubFolderDes, filename)
        return FileResponse(safe_file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3002, log_level='info', reload=True)