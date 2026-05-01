from data_manager import DataManager
dm = DataManager()
books = dm.get_all_books()
epub = [b for b in books if b.file_type == 'epub'][0]
print(f"Book: {epub.title}")
toc = dm.get_epub_toc(epub.id)
print(f"Chapters: {len(toc)}")
for i, c in enumerate(toc[:10]):
    title = c['title'][:40]
    size = len(c['content'])
    print(f"  {i+1}. {title}... ({size} chars)")
