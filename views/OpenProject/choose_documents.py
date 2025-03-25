from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox, QPushButton, QHeaderView, \
    QMessageBox, QHBoxLayout, QSizePolicy, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from views.OpenProject.project_window import ProjectWindow

class ChooseDocuments(QDialog):
    """Dialog for selecting documents related to selected books."""

    def __init__(self, book_data, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Documents")
        self.resize(800, 600)
        self.setModal(True)
        self.selected_documents = []
        self.project_id = project_id
        self.book_data = book_data #book[book.id] = {"name":"", "documents":[]}
        self.all_rows = []

        self.setObjectName("ChooseDocuments")  # For QSS styling

        main_layout = QVBoxLayout()

        # Filter Layout
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Document Name...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        self.release_state_combo = QComboBox()
        self.release_state_combo.addItem("All States")
        self.release_state_combo.addItems(["Draft", "Created", "Released", "Approved", "Archived"])
        self.release_state_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.release_state_combo)

        main_layout.addLayout(filter_layout)

        # Create Table with Dynamic Rows (One Document per Row)
        row_count = sum(len(docs) for docs in book_data.values())
        self.project_table = QTableWidget(row_count, 7)
        self.project_table.setHorizontalHeaderLabels([
            "Book", "Document", "Description", "Revision", "Owner", "State", "Select"
        ])
        self.checkboxes = []
        row = 0

        for book_id, book_info in self.book_data.items():
            book_name = book_info["book_name"]
            documents = book_info["documents"]

            for doc_index, doc in enumerate(documents):  # Now iterating over documents list
                document_name = doc.name
                doc_description = doc.description or ""
                doc_revision = doc.revision or ""
                doc_owner = doc.owner or ""
                doc_state = doc.state or ""

                if doc_index == 0:
                    book_item = QTableWidgetItem(book_name)
                    book_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.project_table.setItem(row, 0, book_item)
                else:
                    empty_item = QTableWidgetItem("")
                    empty_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.project_table.setItem(row, 0, empty_item)

                # Document Name
                doc_item = QTableWidgetItem(document_name)
                doc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.project_table.setItem(row, 1, doc_item)

                # Document Description
                desc_item = QTableWidgetItem(doc_description)
                desc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.project_table.setItem(row, 2, desc_item)

                # Document Revision
                rev_item = QTableWidgetItem(doc_revision)
                rev_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.project_table.setItem(row, 3, rev_item)

                # Document Owner
                owner_item = QTableWidgetItem(doc_owner)
                owner_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.project_table.setItem(row, 4, owner_item)

                # Document State
                state_item = QTableWidgetItem(doc_state)
                state_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.project_table.setItem(row, 5, state_item)


                # Add Checkbox
                checkbox = QCheckBox()
                self.checkboxes.append(checkbox)
                self.project_table.setCellWidget(row, 6, checkbox)

                self.project_table.setRowHeight(row, 40)
                row += 1
        header = self.project_table.horizontalHeader()

        # Make 'Books' column fit contents and stay small
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # Make 'Documents' column interactive for resizing
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)

        # Make 'Description' column fit content size properly
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Make 'Revision', 'Owner', 'State' columns interactive
        for i in range(3, 6):  # Columns 3 to 5
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        # Make 'Select' column interactive but limit its size
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        self.project_table.setColumnWidth(6, 50)  # Set initial width for 'Select' column to 50


        self.project_table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.project_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.project_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.project_table)

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        # Back Button
        self.close_btn = QPushButton("Back")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setFixedHeight(100)
        self.close_btn.setMinimumWidth(200)
        self.close_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.close_btn)

        # Select All Button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_documents)
        self.select_all_btn.setFixedHeight(100)
        self.select_all_btn.setMinimumWidth(200)
        self.select_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.select_all_btn)

        # Deselect All Button
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_documents)
        self.deselect_all_btn.setFixedHeight(100)
        self.deselect_all_btn.setMinimumWidth(200)
        self.deselect_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.deselect_all_btn)

        # Next Button
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.collect_selected_documents)
        self.next_btn.setFixedHeight(100)
        self.next_btn.setMinimumWidth(200)
        self.next_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.next_btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        selected_state = self.release_state_combo.currentText()

        row = 0
        for book_name, documents in self.book_data.items():
            for doc_index, doc in enumerate(documents):
                document_name = doc.name
                doc_state = doc.state or ""

                # Check if the document name matches the search text
                text_match = search_text in document_name.lower()

                # Check if the document state matches the selected state filter
                state_match = (selected_state == "All States" or selected_state == doc_state)

                # If both conditions are true, show the row; otherwise, hide it
                if text_match and state_match:
                    self.project_table.setRowHidden(row, False)
                else:
                    self.project_table.setRowHidden(row, True)

                row += 1

    def select_all_documents(self):
        """Mark all checkboxes as checked."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all_documents(self):
        """Uncheck all checkboxes."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

    def collect_selected_documents(self):
        selected_documents = {}
        row = 0

        for book_id, book_info in self.book_data.items():
            book_name = book_info["book_name"]
            documents = book_info["documents"]

            selected_documents[book_id] = {
                "book_name": book_name,
                "documents": []
            }
            print(selected_documents)
            for document in documents:
                if self.checkboxes[row].isChecked():
                    selected_documents[book_id]["documents"].append(document)  # Adding the full document object
                row += 1

        if not any(book["documents"] for book in selected_documents.values()):
            QMessageBox.warning(self, 'No Document Selected', 'Please select at least one document to continue.')
            return

        # Open the ProjectWindow with the selected documents
        project_window = ProjectWindow(self.project_id, selected_documents, self)
        project_window.exec()

    def get_selected_documents(self):
        return self.selected_documents
