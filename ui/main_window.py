import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager import DataManager
from file_importer import FileImporter
from ui.dialogs import BookEditDialog, ConfirmDialog, ImportDialog
from ui.reader_window import ReaderWindow


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图舒图书管理系统")
        self.root.geometry("900x600")

        self.data_manager = DataManager()
        self.selected_book_id = None

        self._setup_ui()
        self.refresh_book_list()

    def _setup_ui(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(toolbar, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(toolbar, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search())

        tk.Button(toolbar, text="添加", command=self.on_add_book).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="导入TXT", command=lambda: self.on_import("txt")).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="导入EPUB", command=lambda: self.on_import("epub")).pack(side=tk.LEFT, padx=5)

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "title", "author", "type")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="书名")
        self.tree.heading("author", text="作者")
        self.tree.heading("type", text="类型")

        self.tree.column("id", width=50)
        self.tree.column("title", width=300)
        self.tree.column("author", width=200)
        self.tree.column("type", width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_book)
        self.tree.bind("<Double-Button-1>", lambda e: self.on_read_book())

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="修改", command=self.on_edit_book).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除", command=self.on_delete_book).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="阅读", command=self.on_read_book).pack(side=tk.LEFT, padx=5)

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
            self.tree.insert("", tk.END, values=(book.id[:8], book.title, book.author, file_type))

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
            values = item["values"]
            self.selected_book_id = values[0]

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

        content = self.data_manager.get_book_content(book.id)
        if not content:
            messagebox.showerror("错误", "无法读取图书内容")
            return

        reader = ReaderWindow(self.root, book.title, content)
        reader.set_title(book.title)
        reader.show_page()

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
                book = self.data_manager.add_book(final_title, final_author)
                book.file_path = file_path
                book.file_type = file_type
                book.content = content
                from storage import Storage
                storage = Storage()
                storage.save()
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
