import json
import os
import uuid
from datetime import datetime
from typing import List, Optional


class Book:
    def __init__(
        self,
        title: str,
        author: str = "",
        file_path: str = "",
        file_type: str = "none",
        content: str = "",
        book_id: str = None,
        created_at: str = None
    ):
        self.id = book_id or str(uuid.uuid4())
        self.title = title
        self.author = author
        self.file_path = file_path
        self.file_type = file_type
        self.content = content
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(
            book_id=data.get("id"),
            title=data.get("title", ""),
            author=data.get("author", ""),
            file_path=data.get("file_path", ""),
            file_type=data.get("file_type", "none"),
            content=data.get("content", ""),
            created_at=data.get("created_at")
        )


class Storage:
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "books.json"
            )
        self.storage_path = storage_path
        self.books: List[Book] = []
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.books = [Book.from_dict(b) for b in data]
            except (json.JSONDecodeError, IOError):
                self.books = []
        else:
            self.books = []

    def save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=2)

    def add_book(self, book: Book) -> Book:
        self.books.append(book)
        self.save()
        return book

    def get_book(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def update_book(self, book_id: str, title: str = None, author: str = None) -> Optional[Book]:
        book = self.get_book(book_id)
        if book:
            if title is not None:
                book.title = title
            if author is not None:
                book.author = author
            self.save()
        return book

    def delete_book(self, book_id: str) -> bool:
        for i, book in enumerate(self.books):
            if book.id == book_id:
                del self.books[i]
                self.save()
                return True
        return False

    def search_books(self, keyword: str) -> List[Book]:
        if not keyword:
            return self.books
        keyword_lower = keyword.lower()
        return [
            book for book in self.books
            if keyword_lower in book.title.lower() or keyword_lower in book.author.lower()
        ]

    def get_all_books(self) -> List[Book]:
        return self.books
