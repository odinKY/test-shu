# LZ的图书管理系统

基于 Tkinter 的桌面图书管理工具，支持 TXT/EPUB 文件导入、图书管理、阅读器功能。

## 功能特性

### 图书管理
- 手动添加图书（书名、作者）
- 删除图书（带二次确认）
- 修改图书信息
- 按书名/作者模糊搜索

### 文件导入
- **TXT 导入**：自动从文件名或首行提取书名，存储文件路径
- **EPUB 导入**：提取元数据（书名、作者）和章节内容

### 阅读器
- 后台线程异步加载，避免大文件卡顿 UI
- EPUB 左侧目录面板，点击章节跳转
- 上一页 / 下一页翻页
- 字体大小调节（A- / A+）
- 键盘快捷键支持

### 数据存储
- JSON 文件持久化（`books.json`）
- 图书元数据独立存储

## 安装依赖

```bash
pip install customtkinter ebooklib beautifulsoup4 lxml
```

或运行自动安装脚本：

```bash
python install_deps.py
```

## 运行

```bash
python main.py
```

## 项目结构

```
tushu/
├── main.py              # 程序入口
├── storage.py           # 数据模型 + JSON 存储
├── data_manager.py      # 图书业务逻辑
├── file_importer.py     # TXT/EPUB 解析
├── ui/
│   ├── main_window.py   # 主窗口
│   ├── dialogs.py      # 对话框
│   └── reader_window.py # 阅读器窗口
└── books.json           # 数据存储
```

## 快捷键（阅读器）

| 按键 | 功能 |
|------|------|
| `←` / `→` | 上一页 / 下一页 |
| `PgUp` / `PgDn` | 上一页 / 下一页 |
| `Ctrl+←` / `Ctrl+→` | 上一章 / 下一章（EPUB） |
| `Ctrl++` / `Ctrl+-` | 增大 / 减小字体 |
| `Ctrl+0` | 恢复默认字号 |
| `Esc` | 关闭阅读器 |

## 技术栈

- **界面框架**：CustomTkinter
- **EPUB 解析**：ebooklib + BeautifulSoup4
- **数据存储**：JSON
- **Python**：3.8+
