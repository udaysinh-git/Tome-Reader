import os
import shutil
import zipfile
import json
from book import Book
from func import generate_unique_id
from db.database import execute_query

def process_book(file_path, dest, epubFolder):
    try:
        book_id = generate_unique_id(8)
        dest_folder = os.path.join(dest, book_id)
        epub_dest = os.path.join(epubFolder, book_id)
        # Copy, extract and remove temporary zip
        shutil.copy(file_path, dest_folder + ".zip")
        shutil.copy(file_path, epub_dest + ".epub")
        with zipfile.ZipFile(dest_folder + ".zip", "r") as zip_ref:
            zip_ref.extractall(dest_folder)
        os.remove(dest_folder + ".zip")
        
        bk = Book(file_path, dest)
        bk.get_cover(book_id)
        bk.get_chapters(book_id)
        
        # Check for duplicate book by name
        row = execute_query("SELECT id FROM Books WHERE name = ?", (bk.name,), fetchone=True)
        if row:
            shutil.rmtree(dest_folder)
            os.remove(epub_dest + ".epub")
            return "duplicate"
        
        chapters_str = json.dumps(bk.chapters) if bk.chapters else ""
        execute_query(
            "INSERT INTO Books (id, name, cover, base, chapters) VALUES (?, ?, ?, ?, ?)",
            (book_id, bk.name, bk.cover, dest_folder, chapters_str),
            commit=True
        )
        return "done"
    except Exception as error:
        print(f"Error processing {file_path}: {error}")
        return "error"
