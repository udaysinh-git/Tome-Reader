import sys
import os
import shutil
from db.database import EPUB_FOLDER

def process_epub_folder(base_path, epubFolder=EPUB_FOLDER, book_files=[]):
    for book in book_files:
        book_id = book['id']
        src_epub = os.path.join(base_path, book['filePath']) + '.epub'
        dest_epub = os.path.join(epubFolder, book_id) + '.epub'
        if os.path.exists(src_epub):
            try:
                shutil.copy(src_epub, dest_epub)
                print(f"Copied {src_epub} to {dest_epub}")
            except Exception as e:
                print(f"Error copying {src_epub}: {e}")
        else:
            print(f"File {src_epub} not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: addEpubFolder.py /path/to/base")
        sys.exit(1)
    base = sys.argv[1]
    book_files = []
    process_epub_folder(base, EPUB_FOLDER, book_files)
