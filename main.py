import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

import os

def load_stylesheet(app, filename="styles.qss"):
    """Loads QSS stylesheet from an external file."""
    stylesheet_path = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"⚠️ Stylesheet not found: {stylesheet_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
