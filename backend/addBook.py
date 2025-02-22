import os
import zipfile
import shutil
import json
from book import Book
from func import generate_unique_id
from db.database import get_db, execute_query, BOOKS_FOLDER, EPUB_FOLDER
from book_utils import process_book

def AddBook(file_path, dest=BOOKS_FOLDER, epubFolder=EPUB_FOLDER):
    result = process_book(file_path, dest, epubFolder)
    if result == "duplicate":
        return "Book already exists"
    return result
