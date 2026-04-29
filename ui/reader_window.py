import tkinter as tk
from tkinter import scrolledtext, ttk


class ReaderWindow(tk.Toplevel):
    def __init__(self, parent, title: str, content: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x600")
        self.content = content
        self.current_page = 0
        self.pages = []
        self.lines_per_page = 50

        self._setup_ui()
        self._paginate_content()

    def _setup_ui(self):
        self.title_label = tk.Label(self, text=self.title(), font=("Arial", 14, "bold"))
        self.title_label.pack(pady=10)

        nav_frame = tk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)

        self.prev_btn = tk.Button(nav_frame, text="上一页", command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT)

        self.page_label = tk.Label(nav_frame, text="")
        self.page_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = tk.Button(nav_frame, text="下一页", command=self.next_page)
        self.next_btn.pack(side=tk.RIGHT)

        self.text_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Arial", 12)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED)

        close_frame = tk.Frame(self)
        close_frame.pack(fill=tk.X, padx=10, pady=5)

        self.close_btn = tk.Button(close_frame, text="关闭", command=self.destroy)
        self.close_btn.pack(side=tk.RIGHT)

    def _paginate_content(self):
        lines = self.content.split('\n')
        self.pages = []
        for i in range(0, len(lines), self.lines_per_page):
            page_content = '\n'.join(lines[i:i + self.lines_per_page])
            self.pages.append(page_content)

        if not self.pages:
            self.pages = [""]

    def show_page(self):
        if 0 <= self.current_page < len(self.pages):
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, self.pages[self.current_page])
            self.text_area.config(state=tk.DISABLED)

            total_pages = len(self.pages)
            self.page_label.config(text=f"第 {self.current_page + 1} / {total_pages} 页")

            self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.show_page()

    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title
        if hasattr(self, 'title_label'):
            self.title_label.config(text=title)

    def show(self):
        self.set_title(self.title())
        self.show_page()
        self.wait_window()
