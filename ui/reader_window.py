import customtkinter as ctk
import tkinter as tk
import threading
import re


class ReaderWindow(ctk.CTkToplevel):
    LINES_PER_PAGE = 35
    FONT_SIZES = [11, 12, 13, 14, 15, 16, 18, 20]
    DEFAULT_FONT_SIZE = 13

    def __init__(self, parent, book_title: str, book_id: str, file_type: str, data_manager):
        super().__init__(parent)
        self._book_title = book_title
        self._book_id = book_id
        self._file_type = file_type
        self._data_manager = data_manager

        self.title(book_title)
        self.geometry("1050x720")
        self.minsize(700, 450)

        self._chapters = []
        self._current_chapter = 0
        self._pages = []
        self._current_page = 0
        self._font_index = self.FONT_SIZES.index(self.DEFAULT_FONT_SIZE)
        self._destroyed = False
        self._loading = True

        self._setup_ui()
        self._bind_keys()
        self._start_loading()

    # ==================== UI ====================

    def _setup_ui(self):
        top_bar = ctk.CTkFrame(self, height=40)
        top_bar.pack(fill="x", padx=8, pady=(8, 0))
        top_bar.pack_propagate(False)

        self._chapter_label = ctk.CTkLabel(
            top_bar, text=self._book_title,
            font=("Microsoft YaHei", 14, "bold"), anchor="w"
        )
        self._chapter_label.pack(side="left", padx=10, fill="x", expand=True)

        self._font_small_btn = ctk.CTkButton(
            top_bar, text="A-", width=30, height=28,
            command=self._decrease_font
        )
        self._font_small_btn.pack(side="right", padx=2)

        self._font_big_btn = ctk.CTkButton(
            top_bar, text="A+", width=30, height=28,
            command=self._increase_font
        )
        self._font_big_btn.pack(side="right", padx=2)

        ctk.CTkButton(
            top_bar, text="关闭", command=self.destroy, width=50, height=28
        ).pack(side="right", padx=(10, 5))

        if self._file_type == "epub":
            self._setup_epub_layout()
        else:
            self._setup_simple_layout()

    def _setup_epub_layout(self):
        self._paned = tk.PanedWindow(
            self, orient=tk.HORIZONTAL,
            sashrelief=tk.RAISED, sashwidth=3, bg="#555"
        )
        self._paned.pack(fill="both", expand=True, padx=8, pady=8)

        left = ctk.CTkFrame(self._paned, width=220)
        self._paned.add(left, minsize=150, width=220)

        toc_header = ctk.CTkFrame(left, height=36)
        toc_header.pack(fill="x", padx=5, pady=(8, 0))
        toc_header.pack_propagate(False)
        ctk.CTkLabel(
            toc_header, text="📖 目录",
            font=("Microsoft YaHei", 13, "bold")
        ).pack(side="left", padx=5)

        list_container = ctk.CTkFrame(left, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=5, pady=5)

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        self._chapter_listbox = tk.Listbox(
            list_container,
            font=("Microsoft YaHei", 11),
            bg="#2b2b2b" if is_dark else "#f5f5f5",
            fg="#dcdcdc" if is_dark else "#333333",
            selectbackground="#1f538b",
            selectforeground="#ffffff",
            borderwidth=0, highlightthickness=0,
            activestyle="none", exportselection=False
        )
        scrollbar = ctk.CTkScrollbar(list_container, command=self._chapter_listbox.yview)
        self._chapter_listbox.configure(yscrollcommand=scrollbar.set)
        self._chapter_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._chapter_listbox.bind("<<ListboxSelect>>", self._on_chapter_select)

        right = ctk.CTkFrame(self._paned)
        self._paned.add(right, stretch="always")
        self._build_text_panel(right)

    def _setup_simple_layout(self):
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=8, pady=8)
        self._build_text_panel(container)

    def _build_text_panel(self, parent):
        nav = ctk.CTkFrame(parent, height=36)
        nav.pack(fill="x", padx=5, pady=(5, 0))
        nav.pack_propagate(False)

        self._prev_btn = ctk.CTkButton(
            nav, text="◀ 上一页", command=self._prev_page, width=80, height=28
        )
        self._prev_btn.pack(side="left")
        self._prev_btn.configure(state="disabled")

        self._page_label = ctk.CTkLabel(nav, text="加载中...")
        self._page_label.pack(side="left", expand=True)

        self._next_btn = ctk.CTkButton(
            nav, text="下一页 ▶", command=self._next_page, width=80, height=28
        )
        self._next_btn.pack(side="right")
        self._next_btn.configure(state="disabled")

        text_frame = ctk.CTkFrame(parent)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self._text_area = ctk.CTkTextbox(
            text_frame, wrap="word",
            font=("Microsoft YaHei", self.DEFAULT_FONT_SIZE)
        )
        self._text_area.pack(fill="both", expand=True)
        self._text_area.configure(state="disabled")

    # ==================== 键盘绑定 ====================

    def _bind_keys(self):
        self.bind("<Left>", lambda e: self._prev_page())
        self.bind("<Right>", lambda e: self._next_page())
        self.bind("<Prior>", lambda e: self._prev_page())
        self.bind("<Next>", lambda e: self._next_page())
        self.bind("<Control-Left>", lambda e: self._prev_chapter())
        self.bind("<Control-Right>", lambda e: self._next_chapter())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-plus>", lambda e: self._increase_font())
        self.bind("<Control-minus>", lambda e: self._decrease_font())
        self.bind("<Control-0>", lambda e: self._reset_font())

    # ==================== 异步加载 ====================

    def _start_loading(self):
        self._set_text("⏳ 正在加载，请稍候...")

        def load():
            try:
                if self._file_type == "epub":
                    self._chapters = self._data_manager.get_epub_toc(self._book_id)
                    if not self._chapters:
                        content = self._data_manager.get_book_content(self._book_id)
                        self._chapters = [{"title": self._book_title, "content": content or ""}]
                else:
                    content = self._data_manager.get_book_content(self._book_id)
                    if content:
                        self._chapters = [{"title": self._book_title, "content": content}]
                    else:
                        self._chapters = [{
                            "title": "无法读取",
                            "content": "无法读取图书内容，文件可能已被移动或删除。"
                        }]
            except Exception as e:
                self._chapters = [{
                    "title": "加载失败",
                    "content": f"读取图书时出错：{str(e)}"
                }]

            self._safe_after(self._on_content_loaded)

        threading.Thread(target=load, daemon=True).start()

    def _on_content_loaded(self):
        self._loading = False

        if self._file_type == "epub" and hasattr(self, "_chapter_listbox"):
            for ch in self._chapters:
                self._chapter_listbox.insert("end", ch["title"])

        if self._chapters:
            self._show_chapter(0)

    # ==================== 章节导航 ====================

    def _on_chapter_select(self, event=None):
        selection = self._chapter_listbox.curselection()
        if selection:
            self._show_chapter(selection[0])

    def _show_chapter(self, index: int):
        if not (0 <= index < len(self._chapters)):
            return

        self._current_chapter = index
        self._current_page = 0
        chapter = self._chapters[index]

        title = chapter["title"] if self._file_type == "epub" else self._book_title
        self._chapter_label.configure(text=title)

        self._paginate(chapter["content"])

        if self._file_type == "epub" and hasattr(self, "_chapter_listbox"):
            self._chapter_listbox.selection_clear(0, "end")
            self._chapter_listbox.selection_set(index)
            self._chapter_listbox.see(index)

        self._render_page()

    def _prev_chapter(self):
        if self._file_type != "epub" or not hasattr(self, "_chapter_listbox"):
            return
        if self._current_chapter > 0:
            self._show_chapter(self._current_chapter - 1)

    def _next_chapter(self):
        if self._file_type != "epub" or not hasattr(self, "_chapter_listbox"):
            return
        if self._current_chapter < len(self._chapters) - 1:
            self._show_chapter(self._current_chapter + 1)

    # ==================== 分页 ====================

    def _paginate(self, text: str):
        lines = text.split("\n")
        self._pages = []
        for i in range(0, len(lines), self.LINES_PER_PAGE):
            self._pages.append("\n".join(lines[i:i + self.LINES_PER_PAGE]))
        if not self._pages:
            self._pages = [""]

    # ==================== 页面渲染 ====================

    def _render_page(self):
        if not self._pages:
            return

        total = len(self._pages)
        current = self._current_page + 1

        self._text_area.configure(state="normal")
        self._text_area.delete("1.0", "end")
        self._text_area.insert("1.0", self._pages[self._current_page])
        self._text_area.configure(state="disabled")

        self._page_label.configure(text=f"第 {current}/{total} 页")
        self._prev_btn.configure(
            state="normal" if self._current_page > 0 else "disabled"
        )
        self._next_btn.configure(
            state="normal" if self._current_page < total - 1 else "disabled"
        )

    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def _next_page(self):
        if self._current_page < len(self._pages) - 1:
            self._current_page += 1
            self._render_page()

    # ==================== 字体调节 ====================

    def _apply_font(self):
        size = self.FONT_SIZES[self._font_index]
        self._text_area.configure(font=("Microsoft YaHei", size))

    def _increase_font(self):
        if self._font_index < len(self.FONT_SIZES) - 1:
            self._font_index += 1
            self._apply_font()

    def _decrease_font(self):
        if self._font_index > 0:
            self._font_index -= 1
            self._apply_font()

    def _reset_font(self):
        self._font_index = self.FONT_SIZES.index(self.DEFAULT_FONT_SIZE)
        self._apply_font()

    # ==================== 工具方法 ====================

    def _set_text(self, text: str):
        self._text_area.configure(state="normal")
        self._text_area.delete("1.0", "end")
        self._text_area.insert("1.0", text)
        self._text_area.configure(state="disabled")

    def _safe_after(self, callback):
        if not self._destroyed:
            try:
                self.after(0, callback)
            except Exception:
                pass

    def destroy(self):
        self._destroyed = True
        super().destroy()
