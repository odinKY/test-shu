import os


class FileImporter:
    @staticmethod
    def import_txt(file_path: str) -> tuple:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        title = os.path.splitext(os.path.basename(file_path))[0]
        first_line = content.split('\n')[0].strip()
        if first_line and len(first_line) < 100:
            title = first_line

        return title, "", content

    @staticmethod
    def import_epub(file_path: str) -> tuple:
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except ImportError as e:
            raise ImportError(f"Required library not found: {e}")

        book = epub.read_epub(file_path)

        title_items = book.get_metadata('DC', 'title')
        title = os.path.splitext(os.path.basename(file_path))[0]
        if title_items:
            title = title_items[0][0]

        author_items = book.get_metadata('DC', 'creator')
        author = ""
        if author_items:
            author = author_items[0][0]

        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                if text:
                    chapters.append(text)

        content = "\n\n".join(chapters)

        return title, author, content
