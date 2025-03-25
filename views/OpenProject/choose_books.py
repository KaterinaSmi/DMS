from PyQt6.QtWidgets import QDialog, QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QSizePolicy, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from database.db_methods import get_project_by_id, get_books_by_project, get_documents_by_book
from views.OpenProject.choose_documents import ChooseDocuments


class ChooseBooks(QDialog):
    """Dialog displaying project details and list of books with selection capability."""

    def __init__(self, project_id, book_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.resize(800, 600)
        self.setModal(True)
        self.selected_books = []

        main_layout = QVBoxLayout()

        # Load project details
        self.project_id = project_id
        self.project = get_project_by_id(project_id)
        self.books = get_books_by_project(project_id)

        if not self.project:
            print(f"Error: No project found for ID {project_id}")
            return

        # Determine the number of rows needed
        num_rows = max(1, len(self.books))

        # Create Table with Dynamic Rows (One Book per Row)
        self.project_table = QTableWidget(num_rows, 3)  # Now 3 columns
        self.project_table.setHorizontalHeaderLabels(["Product Name", "Books", "Select"])

        # Ensure the Project name only appears in the first row
        name_item = QTableWidgetItem(self.project.name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Read-only format

        self.project_table.setItem(0, 0, name_item)

        # Add books to individual rows under the "Books" column
        self.checkboxes = []
        for row, book in enumerate(self.books):
            book_item = QTableWidgetItem(book.name)
            book_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            book_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

            checkbox = QCheckBox()
            self.checkboxes.append(checkbox)

            self.project_table.setItem(row, 1, book_item)
            self.project_table.setCellWidget(row, 2, checkbox)

        # Enable Scrollbars to Prevent Cutting Off Rows
        self.project_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.project_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Allow interactive resizing of all columns
        header = self.project_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Allow Column Resizing, but Keep Fixed Row Heights
        self.project_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.project_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.project_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Fix Row Height for Readability
        for row in range(num_rows):
            self.project_table.setRowHeight(row, 40)

        # Select All Button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_books)
        self.select_all_btn.setFixedHeight(100)
        self.select_all_btn.setMinimumWidth(200)
        self.select_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")


        # Deselect All Button
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_books)
        self.deselect_all_btn.setFixedHeight(100)
        self.deselect_all_btn.setMinimumWidth(200)
        self.deselect_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")


        # 'Next' Button to Proceed
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.collect_selected_books_to_new_page)
        self.next_btn.setFixedHeight(100)
        self.next_btn.setMinimumWidth(200)
        self.next_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")

        # Close Button (Bottom)
        self.close_btn = QPushButton("Back")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setFixedHeight(100)
        self.close_btn.setMinimumWidth(200)
        self.close_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")

        # Add the table and buttons to the layout
        main_layout.addWidget(self.project_table)
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.close_btn)
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addWidget(self.next_btn)

        main_layout.addLayout(button_layout)


        self.setLayout(main_layout)

    def select_all_books(self):
        """Mark all checkboxes as checked."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all_books(self):
        """Uncheck all checkboxes."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)


    def collect_selected_books_to_new_page(self):
        self.selected_books = [book for book, checkbox in zip(self.books, self.checkboxes) if checkbox.isChecked()]
        if not self.selected_books:
            QMessageBox.warning(self, 'No Book Selected', 'Please select at least one book to continue.')
            return

        # Prepare book_data for the next dialog
        book_data = {}
        for book in self.selected_books:
            if book.project_id == self.project_id:  # Ensuring the project_id matches the current project
                documents = get_documents_by_book(book.id)

                # Save book_name and documents together
                book_data[book.id] = {
                    "book_name": book.name,
                    "documents": documents
                }

        # Open select_documents dialog
        select_documents_dialog = ChooseDocuments(book_data, self.project_id, self)
        select_documents_dialog.exec()


def get_selected_books(self):
        return self.selected_books
