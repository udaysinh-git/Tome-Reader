import os
import shutil
import secrets
import string

def generate_unique_id(length=6):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def bookTemp(book_id, name, cover, base):
    return {
        "id": book_id,
        "Name": name,
        "Cover": cover,
        "base": base,
        "Tags": [],
        "BookMarks": [],
        "Highlights": [],
        "Chapters": []
    }

def delBook(id, dest, epubDes):
    epub_path = os.path.join(epubDes, id) + '.epub'
    book_folder = os.path.join(dest, id)
    if os.path.exists(epub_path):
        os.remove(epub_path)
    if os.path.exists(book_folder):
        shutil.rmtree(book_folder)

def intalise():
    if not os.path.exists("books"):
        os.mkdir("books")
    if not os.path.exists("epubBooks"):
        os.mkdir("epubBooks")
    # Removed creation of 'Database' folder as JSON is no longer in use.