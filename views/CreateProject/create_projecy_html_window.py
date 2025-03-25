from PyQt6 import QtWidgets, QtGui, QtCore
import csv
import os
from PyQt6.QtWidgets import QHeaderView, QToolButton, QMenu, QFileDialog, QMessageBox
from views.CreateProject.book_reorder_dialog import BookReorderDialog


class GroupView(QtWidgets.QTreeView):
    """Tree View for expandable book list."""

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setIndentation(15)
        self.setExpandsOnDoubleClick(False)
        self.clicked.connect(self.on_clicked)
        self.setModel(model)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)

        # Enable Drag-and-Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.dragged_index = None
        print(" GroupView initialized successfully.")

    def on_clicked(self, index):
        """Expands or collapses book data rows when clicking on the book name."""
        try:
            if not index.parent().isValid() and index.column() == 0:
                self.setExpanded(index, not self.isExpanded(index))
                print(f" Clicked index: {index.data()}, Expanded: {self.isExpanded(index)}")

                # Show the reorder dialog when clicking on the book name
                book_name = index.data()
                # Get all books from the model
                books = [self.model().item(i, 0).text() for i in range(self.model().rowCount())]

                dialog = BookReorderDialog(self, book_name=book_name, books=books)
                if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    print(f"New Order for '{book_name}': {dialog.new_order}")

                    # Update the model based on the new order
                    self.update_model_with_new_order(dialog.new_order)

        except Exception as e:
            print(f"Error during expansion/collapse: {e}")

    def update_model_with_new_order(self, new_order):
        """Updates the GroupModel with the new order of books."""
        current_items = []

        for i in range(self.model().rowCount()):
            item = self.model().takeRow(0)
            current_items.append(item)

        # Reorder items according to the new order
        for book_name in new_order:
            for item in current_items:
                if item[0].text() == book_name:
                    self.model().appendRow(item)
                    break

    def startDrag(self, supported_actions):
        """Initiates the drag action."""
        try:

            indexes = self.selectedIndexes()
            self.dragged_index = indexes[0]
            if not self.dragged_index.isValid():
                print(" Dragged index is invalid.")
                self.dragged_index = None
                return

            item_text = self.dragged_index.data()
            print(f" Dragging index: {item_text}")

            # Check if it's a top-level item (Book Title)
            if not self.dragged_index.parent().isValid():
                print(" Top-level item detected (Book Title).")
                print(" Allowing dragging of top-level items.")

                # Initialize QDrag object
                drag = QtGui.QDrag(self)

                # Create mime data object
                mime_data = QtCore.QMimeData()
                mime_data.setText(item_text)

                drag.setMimeData(mime_data)
                drag.setHotSpot(QtCore.QPoint(0, 0))  # Set hotspot to avoid crashes

                # Execute the drag operation
                result = drag.exec(QtCore.Qt.DropAction.MoveAction)
                return  # Safely return after top-level drag
            # Handle normal (non-top-level) dragging
            drag = QtGui.QDrag(self)
            mime_data = self.model().mimeData(indexes)

            if mime_data is None:
                print(" Failed to create mime data.")
                self.dragged_index = None
                return

            drag.setMimeData(mime_data)
            drag.setHotSpot(QtCore.QPoint(0, 0))  # Safe hotspot definition

            # Execute the drag
            result = drag.exec(QtCore.Qt.DropAction.MoveAction)
            print(f" Drag operation result: {result}")

        except Exception as e:
            print(f" Error during startDrag: {e}")

    def dropEvent(self, event):
        """Handles row drop event properly."""
        if self.dragged_index is None:
            event.ignore()
            return

        # Convert position from QPointF to QPoint
        drop_position = event.position().toPoint()
        drop_index = self.indexAt(drop_position)

        if not drop_index.isValid():
            print(" Invalid drop index.")
            event.ignore()
            return

        source_row = self.dragged_index.row()
        target_row = drop_index.row()

        parent_index = self.dragged_index.parent()
        target_parent_index = drop_index.parent()

        print(f" Source Row: {source_row}, Target Row: {target_row}")

        if not parent_index.isValid() and not target_parent_index.isValid():
            # Moving a book (top-level row)
            print(" Handling top-level item drop (Book Title).")
            if self.dragged_index != drop_index:
                try:
                    items = self.model().takeRow(source_row)
                    if not items:
                        print(" Failed to take row from model.")
                        event.ignore()
                        return

                    self.model().insertRow(target_row, items)
                    print(" Successfully moved top-level item (Book).")
                    event.accept()
                except Exception as e:
                    print(f" Error during top-level item drop: {e}")
                    event.ignore()
            else:
                print(" Same position drop detected. Ignored.")
                event.ignore()

        elif parent_index.isValid() and parent_index == target_parent_index:
            # Moving documents within the same book
            print(" Handling document move within the same book.")
            try:
                parent_item = self.model().itemFromIndex(parent_index)
                if parent_item:
                    items = parent_item.takeRow(source_row)
                    parent_item.insertRow(target_row, items)
                    print(" Successfully moved document within the book.")
                    event.accept()
                else:
                    print("Parent item not found.")
                    event.ignore()
            except Exception as e:
                print(f" Error during document move: {e}")
                event.ignore()
        else:
            print(" Drop operation not supported for this case.")
            event.ignore()

        self.dragged_index = None


class GroupModel(QtGui.QStandardItemModel):
    """Tree Model to store books and their data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Book Title"])

    def set_dynamic_columns(self, headers):
        self.setColumnCount(len(headers) + 1)
        self.setHorizontalHeaderLabels(["Title"] + headers)

    def add_book(self, book_name):
        book_item = QtGui.QStandardItem(book_name)
        book_item.setEditable(False)
        self.appendRow([book_item])
        return book_item

    def append_data_to_book(self, book_item, row_data):
        row_idx = book_item.rowCount()
        for col_idx in range(1, self.columnCount()):
            text = row_data[col_idx - 1] if col_idx - 1 < len(row_data) else "-"
            item = QtGui.QStandardItem(text)
            item.setEditable(False)
            book_item.setChild(row_idx, col_idx, item)

class CreateProjectHtml(QtWidgets.QDialog):
    """Main Window for Managing Book Data"""

    def __init__(self, parent=None, project_name="", books_data=None):
        super().__init__(parent)
        self.setWindowTitle(f"Create HTML for {project_name}")
        self.resize(1400, 800)
        self.setModal(True)

        self.project_name = project_name
        self.books_data = books_data if books_data else []

        layout = QtWidgets.QVBoxLayout()

        # Action Menu
        self.create_action_menu(layout)

        # Project Name Label (Editable)
        self.project_label = QtWidgets.QLabel(f"<h2>{self.project_name}</h2>")
        self.project_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.project_label.setStyleSheet("""
            font-size: 24px;
            padding: 12px;
            background: transparent;
        """)
        self.project_label.mousePressEvent = self.edit_project_name
        layout.addWidget(self.project_label)

        # Initial Section Label at the top
        self.section_label = QtWidgets.QLabel("Section 1")
        self.section_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 6px;
            background-color: #f0f0f0;
            border: 1px solid gray;
            color: black;
            text-align: center;
        """)
        self.section_label.mousePressEvent = self.edit_section_name
        self.section_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.section_label)

        # Tree View Setup
        self.model = GroupModel(self)
        self.tree_view = GroupView(self.model)
        layout.addWidget(self.tree_view)

        self.populate_tree()

        self.setLayout(layout)

    def edit_project_name(self, event):
        """Allows the user to edit the project name."""
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Edit Project Name", "Enter Project Name:",
                                                      text=self.project_label.text())
        if ok and new_name:
            self.project_label.setText(new_name)

    def edit_section_name(self, event):
        """Allows the user to edit the project name."""
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Edit Section Name", "Enter Section Name:",
                                                      text=self.section_label.text())
        if ok and new_name:
            self.section_label.setText(new_name)

    def create_action_menu(self, layout):
        self.action_menu = QToolButton(self)
        self.action_menu.setText("☰ Actions")
        self.action_menu.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.action_menu.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        menu = QMenu(self)

        add_section_action = menu.addAction("Add Section")
        add_section_action.triggered.connect(self.add_section)
        add_book_action = menu.addAction("Add Book")
        add_book_action.triggered.connect(self.add_book)
        menu.addAction("Exit").triggered.connect(self.reject)

        self.action_menu.setMenu(menu)
        layout.addWidget(self.action_menu)

    def add_section(self):
        """Add a new section below the table."""
        section_name, ok = QtWidgets.QInputDialog.getText(self, "Add Section", "Enter Section Name:")
        if ok and section_name.strip():
            section_label = QtWidgets.QLabel(section_name)
            section_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                padding: 6px;
                background-color: #f0f0f0;
                border: 1px solid gray;
                color:black;
                text-align: center;
            """)
            section_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)  # Ensures text is centered
            section_label.mousePressEvent = self.edit_section_name

            # Insert the new section at the bottom, just before the table view.
            self.layout().addWidget(section_label)

    def add_book(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Book", "", "CSV Files (*.csv)")
        if not file_path:
            return

        book_name = os.path.basename(file_path)
        book_data = {"name": book_name, "headers": [], "rows": []}

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                book_data["headers"] = next(csv_reader, None)
                book_data["rows"] = [row for row in csv_reader]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read CSV: {e}")
            return

        book_item = self.model.add_book(book_name)
        self.model.set_dynamic_columns(book_data["headers"])

        for row in book_data["rows"]:
            self.model.append_data_to_book(book_item, row)

    def populate_tree(self):
        if not self.books_data:
            return

        first_book = self.books_data[0]
        if "headers" in first_book and first_book["headers"]:
            self.model.set_dynamic_columns(first_book["headers"])

        for book in self.books_data:
            book_item = self.model.add_book(book["name"])
            for row in book["rows"]:
                self.model.append_data_to_book(book_item, row)

    def export_html(self):
        QtWidgets.QMessageBox.information(self, "Export HTML", "Export to HTML feature coming soon!")

    def open_in_excel(self):
        QtWidgets.QMessageBox.information(self, "Excel", "Opening in Excel...")

    def open_in_myworkshop(self):
        QtWidgets.QMessageBox.information(self, "MyWorkshop", "Opening in MyWorkshop...")
