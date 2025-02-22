import os
import zipfile
import shutil
from book import Book
from func import bookTemp, generate_unique_id
import db

def AddBook(filePath, dest, epubFolder):
    book_id = generate_unique_id(8)
    try:
        if filePath.endswith(".epub") and os.path.isfile(filePath) and os.path.isdir(dest):
            fileName = os.path.basename(filePath).replace(".epub", "")
            destFolder = os.path.join(dest, book_id)
            epub_des = os.path.join(epubFolder, book_id)
            # Copy and extract files
            shutil.copy(filePath, destFolder + ".zip")
            shutil.copy(filePath, epub_des + ".epub")
            with zipfile.ZipFile(destFolder + ".zip", "r") as zip_ref:
                zip_ref.extractall(destFolder)
            os.remove(destFolder + ".zip")
            # Book processing
            book = Book("", dest)
            book.get_cover(book_id)
            book.book_data(book_id)
            tempsub = bookTemp(book_id, book.Name, book.Cover, destFolder)
            tempsub["Chapters"] = book.Chapters if book.Chapters else []
            # Check duplicate by name
            existing_books = db.get_all_books()
            add = True
            for b in existing_books:
                if tempsub["Name"] == b["Name"]:
                    add = False
                    break
            if add:
                db.add_book(tempsub)
            else:
                shutil.rmtree(os.path.join(dest, book_id))
                os.remove(epub_des + ".epub")
            return "done"
    except Exception as error:
        print("Error in AddBook:", error)