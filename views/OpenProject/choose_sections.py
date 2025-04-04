from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox, QPushButton, QHeaderView, \
    QMessageBox, QHBoxLayout, QSizePolicy, QLineEdit

from database.db_methods import get_project_details, get_document_details
from views.OpenProject.project_window import ProjectWindow


class ChooseSections(QDialog):
    """Dialog for selecting documents related to selected books."""

    def __init__(self, selected_documents, project_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Subsections")
        self.resize(800, 600)
        self.setModal(True)
        self.project_id = project_id
        self.selected = []

        self.setObjectName("ChooseSubsections")  # For QSS styling

        main_layout = QVBoxLayout()

        # Filter Layout
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        main_layout.addLayout(filter_layout)
        # Load project details
        self.selected_documents = selected_documents
        structured_data = get_project_details(project_id, self.selected_documents)
        project_name = structured_data["project"]["project_name"]
        self.books_data = structured_data["books"]

        # Fetch and attach document details
        for book_id, book_data in self.books_data.items():
            for document in book_data["documents"]:
                document_id = document["document_id"]
                document_details = get_document_details(project_id=project_id, book_id=book_id, document_id=document_id)
                document["details"] = document_details

                #  Ensure book_id and book_name are stored in each document
                document["book_id"] = book_id
                document["book_name"] = book_data["book_name"]

                # Create Table with Dynamic Rows (One Document per Row)
        self.table = QTableWidget(0, 4)  # Start with 0 rows

        self.table.setHorizontalHeaderLabels([
         "Sections", "Subsections", "Documents", "Select"
        ])
        self.checkboxes = []
        rows = 0

        self.sections = self.collect_sections(self.books_data)
        last_section = None
        last_subsection = None

        for section, subsections in self.sections.items():
            for subsection, docs in subsections.items():
                for doc in docs:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    #Section Column
                    if section != last_section:
                        self.table.setItem(row, 0, QTableWidgetItem(section))
                        last_section = section
                    else:
                        self.table.setItem(row, 0, QTableWidgetItem(""))

                    # Subsection column
                    if subsection != last_subsection:
                        self.table.setItem(row, 1, QTableWidgetItem(subsection))
                        last_subsection = subsection
                    else:
                        self.table.setItem(row, 1, QTableWidgetItem(""))

                    self.table.setItem(row, 2, QTableWidgetItem(doc["doc"]))

                    checkbox= QCheckBox()
                    self.checkboxes.append((section, subsections, doc, checkbox))
                    self.table.setCellWidget(row, 3, checkbox)
                    rows += 1

        header = self.table.horizontalHeader()

        # Make 'Section' column fit contents and stay small
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # Make 'Subsection' column interactive for resizing
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Make 'Docs' column fit content size properly
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        #fixed 'Select' row
        self.table.setColumnWidth(3, 50)

        # Fix Row Height for Readability
        for row in range(rows):
            self.table.setRowHeight(row, 40)

        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

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
        self.select_all_btn.clicked.connect(self.select_all_subsections)
        self.select_all_btn.setFixedHeight(100)
        self.select_all_btn.setMinimumWidth(200)
        self.select_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.select_all_btn)

        # Deselect All Button
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_subsections)
        self.deselect_all_btn.setFixedHeight(100)
        self.deselect_all_btn.setMinimumWidth(200)
        self.deselect_all_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.deselect_all_btn)

        # Next Button
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.proceed)
        self.next_btn.setFixedHeight(100)
        self.next_btn.setMinimumWidth(200)
        self.next_btn.setStyleSheet("font-size: 18px; padding: 10px; border-radius: 20px;")
        buttons_layout.addWidget(self.next_btn)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        row = 0

        for section, subsections in self.sections.items():
            for subsection, docs in subsections.items():
                for doc in docs:
                    subsection_match = search_text in subsection.lower()
                    document_match = search_text in doc["title"].lower()

                    if subsection_match or document_match:
                        self.table.setRowHidden(row, False)
                    else:
                        self.table.setRowHidden(row, True)

                    row += 1

    def select_all_subsections(self):
        """Mark all checkboxes as checked."""
        for _, _, _, checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def deselect_all_subsections(self):
        """Mark all checkboxes as checked."""
        for _, _, _, checkbox in self.checkboxes:
            checkbox.setChecked(False)

    @staticmethod
    def collect_sections(books_data):
        """Collects documents and groups them under sections and subsections."""
        sections = {}
        for book_id, book_info in books_data.items():
            for document in book_info["documents"]:
                section = document["section"]
                subsection = document["subsection"]

                if section not in sections:
                    sections[section] = {}

                if subsection not in sections[section]:
                    sections[section][subsection] = []

                sections[section][subsection].append(document)

        return sections

    def proceed(self):
        selected_documents = {}
        row = 0

        for book_id, book_info in self.books_data.items():
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
            QMessageBox.warning(self, "No selections", "Please select at least one document.")
            return

        self.selected = selected_documents
        project_window = ProjectWindow(self.project_id, selected_documents, self)
        project_window.exec()

    def get_selected(self):
        return self.selected
