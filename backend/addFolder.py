import os
import zipfile
import shutil
import json
from book import Book
from func import generate_unique_id
from db.database import execute_query, BOOKS_FOLDER, EPUB_FOLDER
from book_utils import process_book

def AddFolder(path, dest=BOOKS_FOLDER, epubFolder=EPUB_FOLDER):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if file_path.endswith(".epub") and os.path.isfile(file_path):
            result = process_book(file_path, dest, epubFolder)
            if result == "duplicate":
                continue
            # Optionally, log or handle errors if result == "error"