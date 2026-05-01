import os

from storage import Storage, Book
from typing import List, Optional


class DataManager:
    def __init__(self, storage_path: str = None):
        self.storage = Storage(storage_path)

    def add_book(self, title: str, author: str = "", file_path: str = "", file_type: str = "none") -> Book:
        book = Book(title=title, author=author, file_path=file_path, file_type=file_type)
        return self.storage.add_book(book)

    def update_book_meta(self, book_id: str, file_path: str = None, file_type: str = None) -> Optional[Book]:
        book = self.storage.get_book(book_id)
        if book:
            if file_path is not None:
                book.file_path = file_path
            if file_type is not None:
                book.file_type = file_type
            self.storage.save()
        return book

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

    def get_epub_toc(self, book_id: str) -> list:
        book = self.storage.get_book(book_id)
        if not book or book.file_type != "epub" or not book.file_path:
            return []
        if not os.path.exists(book.file_path):
            return []

        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except ImportError:
            return []

        try:
            epub_book = epub.read_epub(book.file_path)
        except Exception:
            return []

        nav_map = {}
        for item in epub_book.toc:
            self._flatten_toc(item, nav_map)

        spine_items = {}
        for item_id, _ in epub_book.spine:
            spine_items[item_id] = True

        chapters = []
        for item_id, _ in epub_book.spine:
            item = epub_book.get_item_with_id(item_id)
            if not item or item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue

            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            if not text:
                continue

            title = nav_map.get(item.file_name, "")
            if not title:
                heading = soup.find(["h1", "h2", "h3", "h4"])
                if heading:
                    title = heading.get_text(strip=True)
            if not title:
                title = f"章节 {len(chapters) + 1}"

            chapters.append({"title": title, "content": text})

        return chapters

    @staticmethod
    def _flatten_toc(toc_item, result: dict):
        if isinstance(toc_item, tuple):
            section = toc_item[0]
            children = toc_item[1] if len(toc_item) > 1 else []
            if hasattr(section, "title") and hasattr(section, "file_name"):
                result[section.file_name] = section.title
            for child in children:
                DataManager._flatten_toc(child, result)
        elif hasattr(toc_item, "title") and hasattr(toc_item, "file_name"):
            result[toc_item.file_name] = toc_item.title

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
