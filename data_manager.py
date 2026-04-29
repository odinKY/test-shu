from storage import Storage, Book
from typing import List, Optional


class DataManager:
    def __init__(self, storage_path: str = None):
        self.storage = Storage(storage_path)

    def add_book(self, title: str, author: str = "") -> Book:
        book = Book(title=title, author=author, file_type="none")
        return self.storage.add_book(book)

    def delete_book(self, book_id: str) -> bool:
        return self.storage.delete_book(book_id)

    def update_book(self, book_id: str, title: str = None, author: str = None) -> Optional[Book]:
        return self.storage.update_book(book_id, title, author)

    def get_book(self, book_id: str) -> Optional[Book]:
        return self.storage.get_book(book_id)

    def search_books(self, keyword: str) -> List[Book]:
        return self.storage.search_books(keyword)

    def get_all_books(self) -> List[Book]:
        return self.storage.get_all_books()

    def import_txt_book(self, file_path: str, title: str = None, author: str = "") -> Book:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]

        book = Book(
            title=title,
            author=author,
            file_path=file_path,
            file_type="txt",
            content=content
        )
        return self.storage.add_book(book)

    def import_epub_book(self, file_path: str, title: str = None, author: str = "") -> Book:
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            raise ImportError("ebooklib is required for EPUB import. Please install it: pip install ebooklib")

        book_content = epub.read_epub(file_path)

        if not title:
            title_items = book_content.get_metadata('DC', 'title')
            if title_items:
                title = title_items[0][0] if title_items else os.path.splitext(os.path.basename(file_path))[0]
            else:
                title = os.path.splitext(os.path.basename(file_path))[0]

        if not author:
            author_items = book_content.get_metadata('DC', 'creator')
            if author_items:
                author = author_items[0][0] if author_items else ""

        chapters = []
        for item in book_content.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                if text:
                    chapters.append(text)

        content = "\n\n".join(chapters)

        book = Book(
            title=title,
            author=author,
            file_path=file_path,
            file_type="epub",
            content=content
        )
        return self.storage.add_book(book)

    def get_book_content(self, book_id: str) -> Optional[str]:
        book = self.storage.get_book(book_id)
        if not book:
            return None

        if book.content:
            return book.content

        if book.file_path and os.path.exists(book.file_path):
            if book.file_type == "txt":
                with open(book.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            elif book.file_type == "epub":
                try:
                    import ebooklib
                    from ebooklib import epub
                except ImportError:
                    return None

                book_content = epub.read_epub(book.file_path)
                chapters = []
                for item in book_content.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(item.get_content(), 'html.parser')
                        text = soup.get_text(separator='\n', strip=True)
                        if text:
                            chapters.append(text)
                return "\n\n".join(chapters)

        if book.file_type == "none":
            return "【提示】这是一条手动录入的图书记录，\n没有关联的文本内容。\n\n如需阅读内容，请通过\"导入TXT\"或\"导入EPUB\"功能重新导入该书。"

        return None


import os
