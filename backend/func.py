import os
import shutil
import secrets
import string

def generate_unique_id(length=6):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def delBook(book_id, dest, epubDes):
    os.remove(os.path.join(epubDes, book_id) + '.epub')
    shutil.rmtree(os.path.join(dest, book_id))
