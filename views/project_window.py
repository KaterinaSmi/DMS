from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt
from database.db_methods import get_project_by_id, get_books_by_project

class ProjectWindow(QDialog):
    """Dialog displaying project details with product name and books in separate rows."""

    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.resize(800, 600)
        self.setModal(True)

        # Main Vertical Layout
        main_layout = QVBoxLayout()

        # Load project details
        project = get_project_by_id(project_id)
        books = get_books_by_project(project_id)

        if not project:
            print(f"ERROR: No project found for ID {project_id}")
            return

        #  Determine the number of rows needed (at least 1 row)
        num_rows = max(1, len(books))

        #  Create Table with Dynamic Rows (One Book per Row)
        self.project_table = QTableWidget(num_rows, 2)  # Dynamic rows, 2 columns
        self.project_table.setHorizontalHeaderLabels(["Product Name", "Books"])  # Set header labels

        #  Enable Drag & Drop
        self.project_table.setDragEnabled(True)
        self.project_table.setAcceptDrops(True)
        self.project_table.viewport().setAcceptDrops(True)
        self.project_table.setDragDropMode(QTableWidget.DragDropMode.InternalMove)  #  Allows reordering rows
        self.project_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)  #  Allows selecting full rows

        #  Ensure the Project Name only appears in the first row
        name_item = QTableWidgetItem(project.name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Read-only

        self.project_table.setItem(0, 0, name_item)  # Place project name in the first row, first column

        # Add books to individual rows under the "Books" column
        for row, book in enumerate(books):
            book_item = QTableWidgetItem(book.name)
            book_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            book_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Read-only

            self.project_table.setItem(row, 1, book_item)  # Add book to the second column

        #  Enable Scrollbars to Prevent Cutting Off Rows
        self.project_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.project_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        #  Allow Column Resizing, but Keep Fixed Row Heights
        self.project_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Product Name
        self.project_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Books Column

        #  Fix Row Heights for Readability
        for row in range(num_rows):
            self.project_table.setRowHeight(row, 40)  # Adjust row height (increase if needed)

        # Button to Save Order
        self.save_order_btn = QPushButton("Save Order")
        self.save_order_btn.clicked.connect(self.save_book_order)

        # Close Button (Bottom)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setFixedHeight(80)
        self.close_btn.setMinimumWidth(200)
        self.close_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 10px;")

        # Add the table and close button to the layout
        main_layout.addWidget(self.project_table)  # Table with product name & books
        main_layout.addWidget(self.save_order_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignCenter)  # Close button at the bottom

        self.setLayout(main_layout)

    def save_book_order(self):
        """Saves the new order of books in memory (not in database)."""
        self.book_order = []
        for row in range(1, self.project_table.rowCount()):  # Skip row 0 (Product Name)
            book_item = self.project_table.item(row, 1)
            if book_item:
                self.book_order.append(book_item.text())

        print(f" New Book Order Saved in Memory: {self.book_order}")  #Stored for final HTML use

    def get_book_order(self):
        """ Returns the current order of books (for final HTML)."""
        return self.book_order