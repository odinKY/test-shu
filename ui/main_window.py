import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import DataManager
from file_importer import FileImporter
from ui.dialogs import BookEditDialog, ConfirmDialog, ImportDialog
from ui.reader_window import ReaderWindow

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("图舒图书管理系统")
        self.root.geometry("900x600")

        self.data_manager = DataManager()
        self.selected_book_id = None

        self._setup_ui()
        self.refresh_book_list()

    def _setup_ui(self):
        toolbar = ctk.CTkFrame(self.root)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(toolbar, text="搜索:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(toolbar, width=250)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        ctk.CTkButton(toolbar, text="添加", command=self.on_add_book, width=70).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="导入TXT", command=lambda: self.on_import("txt"), width=80).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="导入EPUB", command=lambda: self.on_import("epub"), width=80).pack(side="left", padx=5)

        list_frame = ctk.CTkFrame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "author", "type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", selectmode="browse")

        self.tree.heading("title", text="书名")
        self.tree.heading("author", text="作者")
        self.tree.heading("type", text="类型")

        self.tree.column("title", width=350)
        self.tree.column("author", width=200)
        self.tree.column("type", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_book)
        self.tree.bind("<Double-Button-1>", lambda e: self.on_read_book())

        btn_frame = ctk.CTkFrame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="修改", command=self.on_edit_book, width=70).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="删除", command=self.on_delete_book, width=70).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="阅读", command=self.on_read_book, width=70).pack(side="left", padx=5)

    def refresh_book_list(self, books=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if books is None:
            books = self.data_manager.get_all_books()

        type_map = {
            "none": "手动录入",
            "txt": "TXT文本",
            "epub": "EPUB电子书"
        }

        for book in books:
            file_type = type_map.get(book.file_type, book.file_type)
            self.tree.insert("", "end", values=(book.title, book.author, file_type), tags=(book.id,))

    def on_search(self):
        keyword = self.search_entry.get().strip()
        if keyword:
            books = self.data_manager.search_books(keyword)
        else:
            books = self.data_manager.get_all_books()
        self.refresh_book_list(books)

    def on_select_book(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            tags = item.get("tags", [])
            if tags:
                self.selected_book_id = tags[0]

    def on_add_book(self):
        dialog = BookEditDialog(self.root, "添加图书")
        result = dialog.get_result()
        if result:
            title, author = result
            self.data_manager.add_book(title, author)
            self.refresh_book_list()
            messagebox.showinfo("成功", "图书添加成功!")

    def on_edit_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("警告", "请先选择要修改的图书")
            return

        book = self.data_manager.get_book(self.selected_book_id)
        if not book:
            messagebox.showerror("错误", "未找到该图书")
            return

        dialog = BookEditDialog(self.root, "编辑图书", book.title, book.author)
        result = dialog.get_result()
        if result:
            title, author = result
            self.data_manager.update_book(book.id, title, author)
            self.refresh_book_list()
            messagebox.showinfo("成功", "图书修改成功!")

    def on_delete_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("警告", "请先选择要删除的图书")
            return

        book = self.data_manager.get_book(self.selected_book_id)
        if not book:
            messagebox.showerror("错误", "未找到该图书")
            return

        dialog = ConfirmDialog(self.root, "确认删除", f"确定要删除《{book.title}》吗?")
        if dialog.get_result():
            self.data_manager.delete_book(book.id)
            self.selected_book_id = None
            self.refresh_book_list()
            messagebox.showinfo("成功", "图书删除成功!")

    def on_read_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("警告", "请先选择要阅读的图书")
            return

        book = self.data_manager.get_book(self.selected_book_id)
        if not book:
            messagebox.showerror("错误", "未找到该图书")
            return

        ReaderWindow(self.root, book.title, book.id, book.file_type, self.data_manager)

    def on_import(self, file_type: str):
        if file_type == "epub":
            try:
                import ebooklib
            except ImportError:
                messagebox.showerror(
                    "缺少依赖",
                    "EPUB导入功能需要安装 ebooklib 库。\n\n"
                    "请在终端运行以下命令安装:\n"
                    "pip install ebooklib beautifulsoup4 lxml"
                )
                return

        filetypes = []
        if file_type == "txt":
            filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        elif file_type == "epub":
            filetypes = [("EPUB文件", "*.epub"), ("所有文件", "*.*")]

        file_path = filedialog.askopenfilename(
            title=f"选择{file_type.upper()}文件",
            filetypes=filetypes
        )

        if not file_path:
            return

        try:
            if file_type == "txt":
                title, author, content = FileImporter.import_txt(file_path)
            else:
                title, author, content = FileImporter.import_epub(file_path)

            dialog = ImportDialog(self.root, file_type)
            dialog.set_values(title, author)
            result = dialog.get_result()

            if result:
                final_title, final_author = result
                self.data_manager.add_book(final_title, final_author, file_path, file_type)
                self.refresh_book_list()
                messagebox.showinfo("成功", f"{file_type.upper()}文件导入成功!")
        except ImportError as e:
            messagebox.showerror("缺少依赖", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
