import csv

from PyQt6 import QtWidgets, QtGui, QtCore
import os
from PyQt6.QtWidgets import QHeaderView, QToolButton, QMenu, QFileDialog


class GroupDelegate(QtWidgets.QStyledItemDelegate):
    """Handles the plus/minus icons for expanding/collapsing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._plus_icon = QtGui.QIcon("plus.png")   # Expand Icon
        self._minus_icon = QtGui.QIcon("minus.png") # Collapse Icon

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if not index.parent().isValid():
            is_open = bool(option.state & QtWidgets.QStyle.StateFlag.State_Open)
            option.features |= QtWidgets.QStyleOptionViewItem.ViewItemFeature.HasDecoration
            option.icon = self._minus_icon if is_open else self._plus_icon


class GroupView(QtWidgets.QTreeView):
    """Tree View for expandable book list."""
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setIndentation(15)
        self.setExpandsOnDoubleClick(False)
        self.clicked.connect(self.on_clicked)
        self.setItemDelegateForColumn(0, GroupDelegate(self))
        self.setModel(model)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        # Enable Drag-and-Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_clicked(self, index):
        """Expands or collapses book data rows when clicking on the book name."""
        if not index.parent().isValid() and index.column() == 0:
            self.setExpanded(index, not self.isExpanded(index))


class GroupModel(QtGui.QStandardItemModel):
    """Tree Model to store books and their data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)  # Start with 1 column, expand dynamically
        self.setHorizontalHeaderLabels(["Book Title"])  # Default header

    def set_dynamic_columns(self, headers):
        """Dynamically sets the number of columns based on headers in CSV."""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def add_book(self, book_name):
        """Adds a book as a parent row in the tree view."""
        book_item = QtGui.QStandardItem(book_name)
        book_item.setEditable(False)
        self.appendRow([book_item])
        return book_item  # Return reference to parent item

    def append_data_to_book(self, book_item, row_data):
        """Adds book details as child rows (expandable)."""
        row_idx = book_item.rowCount()  # Get current row count under the book

        for col_idx in range(1, self.columnCount()):  # Ensure all columns are filled
            text = row_data[col_idx - 1] if col_idx < len(row_data) else ""  # Handle missing data
            item = QtGui.QStandardItem(text)
            item.setEditable(False)
            book_item.setChild(row_idx, col_idx, item)  # Insert under book parent


class CreateProjectHtml(QtWidgets.QDialog):
    """Main Window for Managing Book Data"""
    def __init__(self, parent=None, project_name="", books_data=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create HTML for {project_name}")
        self.resize(1400, 800)
        self.setObjectName("createProjectHtml")
        self.setModal(True)

        self.project_name = project_name
        self.books_data = books_data if books_data else []

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # **Action Menu at the Top**
        self.create_action_menu(layout)

        # **Project Name Label**
        self.project_label = QtWidgets.QLabel(f"<h2>{self.project_name}</h2>")
        self.project_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.project_label)

        # **Tree View Setup**
        self.model = GroupModel(self)
        self.tree_view = GroupView(self.model)
        self.tree_view.setAlternatingRowColors(True)  # Alternating background colors
        self.tree_view.setRootIsDecorated(False)  # Removes indentation
        self.tree_view.setUniformRowHeights(True)  # Ensures even spacing
        self.tree_view.setIndentation(20)

        self.tree_view.setStyleSheet("""
            QTreeView::item {
                padding: 10px; /* Adds space inside each row */
                min-height: 40px; /* Ensures rows have spacing */
            }
            QTreeView::branch {
                margin-bottom: 10px; /* Adds space between book groups */
            }
            QTreeView::item:selected {
                background-color: transparent; /* Removes blue highlight */
                color: black; /*  Keeps text visible */
                font-weight: bold; /*  Makes selected text more readable */
            }
        """)

        layout.addWidget(self.tree_view)

        # Populate Books
        self.populate_tree()

        # **Button Layout**
        buttons_layout = QtWidgets.QHBoxLayout()

        self.generate_html_btn = QtWidgets.QPushButton("Save as HTML & Open")
        self.generate_html_btn.clicked.connect(self.export_html)
        buttons_layout.addWidget(self.generate_html_btn)

        self.open_excel_btn = QtWidgets.QPushButton("Open in Excel")
        self.open_excel_btn.clicked.connect(self.open_in_excel)
        buttons_layout.addWidget(self.open_excel_btn)

        self.open_workshop_btn = QtWidgets.QPushButton("Open in MyWorkshop")
        self.open_workshop_btn.clicked.connect(self.open_in_myworkshop)
        buttons_layout.addWidget(self.open_workshop_btn)

        # **Add buttons layout**
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def create_action_menu(self, layout):
        """Creates a dropdown action menu at the top."""
        self.action_button = QToolButton()
        self.action_button.setText("☰ Actions")
        self.action_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.action_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")  # Hide dropdown arrow

        menu = QMenu()

        add_book_action = menu.addAction("Add Book")
        add_book_action.triggered.connect(self.add_book)

        add_section_action = menu.addAction("Add Section")
        add_section_action.triggered.connect(self.add_section)

        add_subsection_action = menu.addAction("Add Subsection")
        add_subsection_action.triggered.connect(self.add_subsection)

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.reject)

        self.action_button.setMenu(menu)
        layout.addWidget(self.action_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    def add_book(self):
        """Adds a new book manually."""
        """Opens a file dialog, reads a CSV book file, and adds it dynamically."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Book", "", "CSV Files (*.csv)")
        if not file_path:
            return  # User canceled selection

        book_name = os.path.basename(file_path)
        book_data = {"name": book_name, "headers": [], "rows": []}

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                book_data["headers"] = next(csv_reader, None)  # Read headers
                book_data["rows"] = [row for row in csv_reader]  # Read data
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to read CSV: {e}")
            return

        # Add Book to Tree
        book_item = self.model.add_book(book_data["name"])



        # Add Book Data Rows
        for row in book_data["rows"]:
            self.model.append_data_to_book(book_item, row)

    def add_document(self):
        """Placeholder for adding a document."""
        QtWidgets.QMessageBox.information(self, "Add Document", "Feature in Progress")

    def add_section(self):
        """Placeholder for adding a section."""
        QtWidgets.QMessageBox.information(self, "Add Section", "Feature in Progress")

    def add_subsection(self):
        """Placeholder for adding a subsection."""
        QtWidgets.QMessageBox.information(self, "Add Subsection", "Feature in Progress")

    def populate_tree(self):
        """Reads CSV files and populates the tree view dynamically."""
        if not self.books_data:
            return

        # Set column headers dynamically from first book
        first_book = self.books_data[0]
        if "headers" in first_book and first_book["headers"]:
            self.model.set_dynamic_columns(["Title"] + first_book["headers"])

        for book in self.books_data:
            book_item = self.model.add_book(book["name"])  #  Add Book Title

            #  Add Data Rows
            for row in book["rows"]:
                self.model.append_data_to_book(book_item, row)

    def export_html(self):
        """Exports the tree data to an HTML file."""
        QtWidgets.QMessageBox.information(self, "Success", "HTML Export feature coming soon!")

    def open_in_excel(self):
        """Placeholder for opening in Excel."""
        QtWidgets.QMessageBox.information(self, "Excel", "Opening in Excel... (Feature in Progress)")

    def open_in_myworkshop(self):
        """Placeholder for opening in MyWorkshop."""
        QtWidgets.QMessageBox.information(self, "MyWorkshop", "Opening in MyWorkshop... (Feature in Progress)")
