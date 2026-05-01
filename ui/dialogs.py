import customtkinter as ctk


class BookEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str = "添加图书", book_title: str = "", book_author: str = ""):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x230")
        self.resizable(False, False)
        self.result = None

        self._setup_ui(book_title, book_author)
        self.transient(parent)
        self.grab_set()

    def _setup_ui(self, book_title: str, book_author: str):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="书名:").grid(row=0, column=0, sticky="w", pady=10)
        self.title_entry = ctk.CTkEntry(main_frame, width=250)
        self.title_entry.grid(row=0, column=1, pady=10, padx=10)
        self.title_entry.insert(0, book_title)
        self.title_entry.focus()

        ctk.CTkLabel(main_frame, text="作者:").grid(row=1, column=0, sticky="w", pady=10)
        self.author_entry = ctk.CTkEntry(main_frame, width=250)
        self.author_entry.grid(row=1, column=1, pady=10, padx=10)
        self.author_entry.insert(0, book_author)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.ok_btn = ctk.CTkButton(btn_frame, text="确定", width=100, command=self._on_ok)
        self.ok_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(btn_frame, text="取消", width=100, command=self._on_cancel)
        self.cancel_btn.pack(side="left", padx=5)

    def _on_ok(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        if title:
            self.result = (title, author)
            self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self.result


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str = "确认", message: str = "确定要删除吗?"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)
        self.result = False

        self._setup_ui(message)
        self.transient(parent)
        self.grab_set()

    def _setup_ui(self, message: str):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text=message, wraplength=300).pack(pady=10)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.ok_btn = ctk.CTkButton(btn_frame, text="确定", width=100, command=self._on_ok)
        self.ok_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(btn_frame, text="取消", width=100, command=self._on_cancel)
        self.cancel_btn.pack(side="left", padx=5)

    def _on_ok(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self.result


class ImportDialog(ctk.CTkToplevel):
    def __init__(self, parent, file_type: str):
        super().__init__(parent)
        self.title(f"导入{file_type.upper()}文件")
        self.geometry("420x270")
        self.resizable(False, False)
        self.file_type = file_type
        self.result = None

        self._setup_ui()
        self.transient(parent)
        self.grab_set()

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="书名:").grid(row=0, column=0, sticky="w", pady=10)
        self.title_entry = ctk.CTkEntry(main_frame, width=250)
        self.title_entry.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(main_frame, text="作者:").grid(row=1, column=0, sticky="w", pady=10)
        self.author_entry = ctk.CTkEntry(main_frame, width=250)
        self.author_entry.grid(row=1, column=1, pady=10, padx=10)

        if self.file_type == "epub":
            ctk.CTkLabel(main_frame, text="(书名和作者将从文件自动提取，可手动修改)").grid(
                row=2, column=0, columnspan=2, sticky="w", pady=5
            )
        else:
            ctk.CTkLabel(main_frame, text="(书名从文件名或首行提取，可手动修改)").grid(
                row=2, column=0, columnspan=2, sticky="w", pady=5
            )

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.ok_btn = ctk.CTkButton(btn_frame, text="确定", width=100, command=self._on_ok)
        self.ok_btn.pack(side="left", padx=5)

        self.cancel_btn = ctk.CTkButton(btn_frame, text="取消", width=100, command=self._on_cancel)
        self.cancel_btn.pack(side="left", padx=5)

    def set_values(self, title: str, author: str):
        self.title_entry.insert(0, title)
        self.author_entry.insert(0, author)

    def _on_ok(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        if title:
            self.result = (title, author)
            self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self.result
