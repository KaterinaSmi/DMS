from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QDialog, QHBoxLayout, QListWidget, QInputDialog,  QMenu, QMessageBox
from PyQt6.QtCore import Qt
import os
from PyQt6.QtGui import QFontMetrics, QCursor, QAction
import csv
from PyQt6.QtWidgets import QListWidgetItem

from views.create_projecy_html_window import CreateProjectHtml


class CreateProjectWindow(QDialog):
    """Window for creating a new project"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Project")
        self.resize(1400, 800)
        self.setObjectName("createProjectWindow")
        self.setModal(True)


        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Variable to store book_path
        self.book_paths = []

        # Project Name (editable Label)
        self.project_name_label = QLabel("Click to enter project name")
        self.project_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.project_name_label.setStyleSheet("""
        font-size: 24px;
        padding: 12pz;
        border: 2px dashed gray;
        background: transparent;
        """)
        self.project_name_label.mousePressEvent = self.edit_project_name
        layout.addWidget(self.project_name_label)

        #Wrapper Widget for Book List (Ensures Proper Centring)
        self.books_container = QWidget()
        books_layout = QHBoxLayout()
        books_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Book List (Styled & Centred)
        self.books_list = QListWidget()
        self.books_list.setVisible(False)

        self.books_list.setStyleSheet("""
        QListWidget {
            background: transparent;
            font-size: 18px;
            border:none;
            padding: 10px;  
        }
        QListWidget::item {
            padding: 10px;
            text-align: center;
        }
        QListWidget::item:selected {
            background: transparent;
            color: white;
            border: none;
        }
        """)
        books_layout.addWidget(self.books_list)
        self.books_container.setLayout(books_layout)
        layout.addWidget(self.books_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add books file selection button (for book import)
        self.add_books_btn = QPushButton("Add books")
        self.add_books_btn.clicked.connect(self.add_books)  # Corrected connection
        layout.addWidget(self.add_books_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Continue Button (Hidden Initially)
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.continue_to_next_page)
        self.continue_btn.setVisible(False)
        layout.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Close Button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


        self.setLayout(layout)

    def edit_project_name(self, event):
        """Allows the user to edit the project name."""
        new_name, ok = QInputDialog.getText(self, "Edit Project Name", "Enter Project Name:", text=self.project_name_label.text())
        if ok and new_name:
            self.project_name_label.setText(new_name)


    def add_books(self):
        """Opens a file dialog to add books from desktop and resizes based on book name length."""
        files, _ = QFileDialog.getOpenFileName(self, "Select Books", "", "Book Files (*.pdf *.epub *.txt *.csv)")

        if files:
            book_name = os.path.basename(files).strip()
            book_name = " ".join(book_name.split())  # Normalize spacing

            item = QListWidgetItem(book_name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.books_list.addItem(item)
            # Store the full file path
            self.book_paths.append(files)

            # Enable right-click delete functionality
            self.books_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.books_list.customContextMenuRequested.connect(self.show_context_menu)

            # Calculate the width needed for the longest book name
            font_metrics = QFontMetrics(self.books_list.font())
            book_width = font_metrics.horizontalAdvance(book_name) + 50  # Add padding

            # Get full window width properly
            full_window_width = self.width() - 100  # Leave space for margins

            # Ensure books_list width grows but does not exceed full window width
            adjusted_width = min(book_width, full_window_width)

            # Apply the calculated width
            self.books_list.setFixedWidth(adjusted_width)
            self.books_container.setFixedWidth(adjusted_width)

            # Prevent horizontal scrolling
            self.books_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.books_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.books_list.setVisible(True)
            self.continue_btn.setVisible(True)

    def show_context_menu(self, pos):
        """Displays a right-click context menu to delete selected books."""
        menu = QMenu(self)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_book)
        menu.addAction(delete_action)

        menu.exec(QCursor.pos())  # Show menu at mouse position

    def delete_selected_book(self):
        """Removes the selected book from the list."""
        selected_items = self.books_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a book to delete.")
            return

        for item in selected_items:
            row = self.books_list.row(item)
            self.books_list.takeItem(row)

            #delete the path as well
            del self.book_paths[row]
        # Resize book list dynamically after deletion
        self.resize_books_list()

    def resize_books_list(self):
        """Adjusts the book list width after deletion based on remaining books."""
        if self.books_list.count() == 0:
            self.books_list.setFixedWidth(200)  # Reset to minimum size
            self.books_container.setFixedWidth(200)
            return

        # Get the longest remaining book name
        font_metrics = QFontMetrics(self.books_list.font())
        max_width = max(
            font_metrics.horizontalAdvance(self.books_list.item(i).text()) for i in range(self.books_list.count())) + 50

        # Get full window width
        full_window_width = self.width() - 100

        # Ensure books_list width grows but does not exceed full window width
        adjusted_width = min(max_width, full_window_width)

        # Apply new width
        self.books_list.setFixedWidth(adjusted_width)
        self.books_container.setFixedWidth(adjusted_width)

    def continue_to_next_page(self):
        """Handles navigation to next page and ensures correct CSV file paths are used."""
        project_name = self.project_name_label.text().strip()
        books_data = []  # List to store structured book data

        for i in range(len(self.book_paths)):  # Retrieve stored file paths
            file_path = self.book_paths[i]

            if not os.path.exists(file_path):  #  Ensure file exists before opening
                print(f"Error: File not found - {file_path}")
                QMessageBox.warning(self, "File Not Found", f"Could not find: {file_path}")
                continue

            book_info = {"name": os.path.basename(file_path), "headers": [], "rows": []}

            # Read CSV files and store structured data
            if file_path.lower().endswith('.csv'):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        csv_reader = csv.reader(file)
                        headers = next(csv_reader, None)  # Extract headers (first row)

                        if headers:
                            book_info["headers"] = headers  # Save headers
                            book_info["rows"] = [row for row in csv_reader]  # Read data
                        else:
                            print( f"Warning: No headers found in {file_path}. Skipping file.")
                except Exception as e:
                    print(f" Error reading {file_path}: {e}")

            books_data.append(book_info)

        if not books_data:
            QMessageBox.warning(self, "No Books Added", "Please add at least one book before continuing.")
            return

        # Open the CreateProjectHtml dialog and pass the extracted CSV data
        dialog = CreateProjectHtml(self, project_name, books_data)
        dialog.exec()