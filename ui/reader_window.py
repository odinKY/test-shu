import tkinter as tk
from tkinter import scrolledtext


class ReaderWindow(tk.Toplevel):
    def __init__(self, parent, book_title: str, content: str):
        super().__init__(parent)
        self._book_title = book_title
        self.title(book_title)
        self.geometry("900x700")

        self.content = content
        self.current_page = 0
        self.pages = []
        self.lines_per_page = 35

        self._setup_ui()
        self._paginate_content()
        self._show_page()

    def _setup_ui(self):
        title_frame = tk.Frame(self)
        title_frame.pack(fill=tk.X, padx=15, pady=10)

        self.title_label = tk.Label(
            title_frame,
            text=self._book_title,
            font=("Microsoft YaHei", 14, "bold"),
            anchor="w"
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        nav_frame = tk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=15, pady=5)

        self.prev_btn = tk.Button(nav_frame, text="◀ 上一页", command=self._prev_page, width=10)
        self.prev_btn.pack(side=tk.LEFT)

        self.page_label = tk.Label(nav_frame, text="", width=15)
        self.page_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = tk.Button(nav_frame, text="下一页 ▶", command=self._next_page, width=10)
        self.next_btn.pack(side=tk.RIGHT)

        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 12),
            bg="#fafafa"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        close_frame = tk.Frame(self)
        close_frame.pack(fill=tk.X, padx=15, pady=10)

        self.close_btn = tk.Button(
            close_frame,
            text="关闭",
            command=self.destroy,
            width=10,
            height=1
        )
        self.close_btn.pack(side=tk.RIGHT)

    def _paginate_content(self):
        lines = self.content.split('\n')
        self.pages = []
        for i in range(0, len(lines), self.lines_per_page):
            page_content = '\n'.join(lines[i:i + self.lines_per_page])
            self.pages.append(page_content)

        if not self.pages:
            self.pages = [""]
        elif len(self.pages) == 1:
            self.pages[0] = self.content

    def _show_page(self):
        if 0 <= self.current_page < len(self.pages):
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, self.pages[self.current_page])
            self.text_area.config(state=tk.DISABLED)

            total = len(self.pages)
            current = self.current_page + 1
            self.page_label.config(text=f"{current} / {total}")

            self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_page < total - 1 else tk.DISABLED)

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._show_page()

    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self._show_page()
