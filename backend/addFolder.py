import os
import zipfile
import shutil
from book import Book
from func import bookTemp, generate_unique_id
import db  # new module to interact with SQLite

def AddFolder(pth, dest, epubDes):
    print("in the AddFolder")
    AllFile = os.listdir(pth)
    for fl in AllFile:
        book_id = generate_unique_id(8)
        try:
            filePath = os.path.join(pth, fl)
            if filePath.endswith(".epub") and os.path.isfile(filePath) and os.path.isdir(dest):
                fileName = os.path.basename(filePath).replace(".epub", "")
                destFolder = os.path.join(dest, book_id)
                epub_des = os.path.join(epubDes, book_id)
                try:
                    shutil.copy(filePath, destFolder + ".zip")
                    shutil.copy(filePath, epub_des + ".epub")
                except Exception:
                    print("Error copying file")
                with zipfile.ZipFile(destFolder + ".zip", "r") as zip_ref:
                    zip_ref.extractall(destFolder)
                os.remove(destFolder + ".zip")
                try:
                    book = Book("", dest)
                    book.get_cover(book_id)
                    book.book_data(book_id)
                except Exception as error:
                    print("Book process ERROR:", error)
                add = True
                tempSub = bookTemp(book_id, book.Name, book.Cover, destFolder)
                # Include chapters if available
                tempSub["Chapters"] = book.Chapters if book.Chapters else []
                # Check for duplicate by name using the database
                existing_books = db.get_all_books()
                for b in existing_books:
                    if tempSub["Name"] == b["Name"]:
                        print("already in the database")
                        add = False
                        break
                if add:
                    db.add_book(tempSub)
                else:
                    os.remove(epub_des + ".epub")
                    shutil.rmtree(destFolder)
        except Exception:
            print("Error processing", fl)
            continue