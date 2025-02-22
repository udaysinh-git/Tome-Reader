import os
import shutil
import zipfile
from bs4 import BeautifulSoup

class Book:
    def __init__(self, file_path, dest):
        self.file_path = file_path
        self.dest = dest
        self.cover = None
        self.name = None
        self.chapters = None

    def extract(self, book_id):
        file_name = os.path.basename(self.file_path)
        if file_name.endswith(".epub") and os.path.exists(self.file_path):
            base_name = file_name[:-5]
            dest_folder = os.path.join(self.dest, book_id)
            temp_zip = dest_folder + ".zip"
            shutil.copy(self.file_path, temp_zip)
            with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                zip_ref.extractall(dest_folder)
            os.remove(temp_zip)
            return dest_folder
        raise Exception("Not a valid EPUB file")

    def get_cover(self, book_id):
        # Assuming the extracted folder name is same as book_id.
        book_folder = os.path.join(self.dest, book_id)
        files = os.listdir(book_folder)
        opf_files = [f for f in files if f.endswith(".opf")]
        if opf_files:
            opf_file_path = os.path.join(book_folder, opf_files[0])
            with open(opf_file_path, "r", encoding="utf-8") as opf_file:
                soup = BeautifulSoup(opf_file, "xml")
                book_title = soup.find("dc:title")
                self.name = book_title.text.strip() if book_title else "Unknown"
                meta_cover = soup.find("meta", attrs={"name": "cover"})
                if meta_cover:
                    cover_id = meta_cover.get("content")
                    pic = soup.find("item", attrs={"id": cover_id})
                    if pic:
                        href = pic.get("href")
                        cover_path = os.path.join(book_folder, href)
                        self.cover = os.path.abspath(cover_path)
                        return self.cover
        self.cover = "NotFound"
        return self.cover

    def get_chapters(self, book_id):
        book_folder = os.path.join(self.dest, book_id)
        files = os.listdir(book_folder)
        ncx_files = [f for f in files if f.endswith(".ncx")]
        if ncx_files:
            ncx_file_path = os.path.join(book_folder, ncx_files[0])
            with open(ncx_file_path, "r", encoding="utf-8") as ncx_file:
                soup = BeautifulSoup(ncx_file, "xml")
                nav_points = soup.select("navMap navPoint")
                chapters = []
                for point in nav_points:
                    label = point.find("navLabel").get_text(strip=True)
                    link = point.find("content")["src"]
                    chapters.append({
                        "name": label,
                        "link": os.path.join(book_folder, link).replace("\\", "/")
                    })
                self.chapters = chapters
                return chapters
        return []
