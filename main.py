import sys
import os
import site

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

usersite = site.getusersitepackages()
if usersite and os.path.exists(usersite) and usersite not in sys.path:
    sys.path.append(usersite)

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
