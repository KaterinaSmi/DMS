from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, \
    QPushButton, QHBoxLayout, QToolButton, QMenu, QScrollArea, QWidget, QInputDialog
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets, QtCore
from database.db_methods import get_project_by_id, get_project_details, get_document_details


class ProjectWindow(QDialog):
    """Dialog displaying project details with product name, sections, and books/documents."""

    def __init__(self, project_id, selected_documents, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.resize(1000, 800)
        self.setModal(True)

        # Create a scrollable main layout
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # The widget holding the scrollable content
        scroll_content = QWidget()
        self.main_layout = QVBoxLayout(scroll_content)

        # Load project details
        self.selected_documents = selected_documents
        structured_data = get_project_details(project_id, self.selected_documents)
        project_name = structured_data["project"]["project_name"]
        books_data = structured_data["books"]

        # Fetch and attach document details
        for book_id, book_data in books_data.items():
            for document in book_data["documents"]:
                document_id = document["document_id"]
                document_details = get_document_details(project_id=project_id, book_id=book_id, document_id=document_id)
                document["details"] = document_details  # Attach details to the document

        # Project Title
        self.project_label = QLabel(f"<h1>{project_name}</h1>")
        self.project_label.setStyleSheet("color: #4D4D4D;")
        self.project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.project_label)

        # Action Menu
        self.create_action_menu()

        # Display sections and documents
        self.display_sections(books_data)

        # Apply the scrollable content to the scroll area
        scroll_area.setWidget(scroll_content)

        # Add scroll area to the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)

    def create_action_menu(self):
        self.action_menu = QToolButton(self)
        self.action_menu.setText("☰ Actions")
        self.action_menu.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        # Apply Styling
        self.action_menu.setStyleSheet("""
               QToolButton {
                   border: 1px solid #4D4D4D;  /* Slightly darker border */
                   border-radius: 10px;  /* Rounded corners */
                   padding: 5px 10px;
                   font-size: 14px;
                   text-align:left;
               }

               QToolButton:hover {
                   background-color: #808080;  /* Lighter on hover */
               }

               QToolButton:pressed {
                   background-color: #4D4D4D;  /* Darker when pressed */
               }

               QToolButton::menu-indicator { 
                   image: none;  /* Removes the default arrow */
               }
           """)
        menu = QMenu(self)

        menu.addAction("Export to HTML").triggered.connect(self.export_html)
        menu.addAction("Open in Excel").triggered.connect(self.open_in_excel)
        menu.addAction("Open in MyWorkshop").triggered.connect(self.open_in_myworkshop)
        menu.addAction("Exit").triggered.connect(self.reject)

        self.action_menu.setMenu(menu)
        self.main_layout.addWidget(self.action_menu)

    def display_sections(self, books_data):
        """Displays sections, subsections, and related documents."""
        sections = self.collect_sections(books_data)

        # Columns to exclude from displaying
        columns_to_exclude = {"project_id", "relation_id", "document_id", "document_detail_id", "active"}

        for section_name, subsections in sections.items():
            # Create section label
            section_label = QLabel(f"<h2>{section_name}</h2>")
            section_label.setStyleSheet("color:#4D4D4D")
            section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            section_label.mousePressEvent = lambda event, label=section_label: self.edit_label(event, label)
            self.main_layout.addWidget(section_label)

            for subsection_name, documents in subsections.items():
                # Create subsection label
                subsection_label = QLabel(f"    ➜ {subsection_name}")
                subsection_label.setStyleSheet("padding-left: 20px; color: #4D4D4D ;")
                subsection_label.mousePressEvent = lambda event, label=subsection_label: self.edit_label(event, label)
                self.main_layout.addWidget(subsection_label)

                # Create Table for Documents
                table = QTableWidget()
                table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                table.setStyleSheet("background-color: white;")
                table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
                table.verticalHeader().setVisible(False)

                # Initialize table row count
                table.setRowCount(len(documents))

                # To store all milestone columns for this subsection
                all_milestone_columns = set()

                for document in documents:
                    document_details = document.get("details", [])
                    if document_details:
                        for detail in document_details:
                            all_milestone_columns.update(
                                [col for col in detail.keys() if col not in columns_to_exclude]
                            )

                all_milestone_columns = list(all_milestone_columns)
                milestone_count = len(all_milestone_columns)

                # Define column count for each document's row (+1 for an expanding filler column)
                column_count = 6 + milestone_count
                table.setColumnCount(column_count)

                # Add headers including milestone columns
                table.setHorizontalHeaderLabels(
                    ["Document", "Title", "State", "Owner", "Release Date"] + all_milestone_columns + [""]
                )

                # Enable resizing of columns
                header = table.horizontalHeader()
                header.setSectionsMovable(True)
                header.setStretchLastSection(True)

                # Set the width of 'Title' column to a fixed size of 350px
                table.setColumnWidth(1, 350)

                # Make all other columns interactive for resizing
                for col_index in range(column_count - 1):  # Excluding the last filler column
                    if col_index != 1:  # Only 'Title' column has fixed width
                        header.setSectionResizeMode(col_index, QHeaderView.ResizeMode.Interactive)

                # Fill rows
                for row_index, document in enumerate(documents):
                    table.setItem(row_index, 0, QTableWidgetItem(document.get("doc", "") or ""))
                    table.setItem(row_index, 1, QTableWidgetItem(document.get("title", "") or ""))
                    table.setItem(row_index, 2, QTableWidgetItem(document.get("state", "") or ""))
                    table.setItem(row_index, 3, QTableWidgetItem(document.get("owner", "") or ""))
                    table.setItem(row_index, 4, QTableWidgetItem(str(document.get("release_date", "")) or ""))

                    # Populate milestone columns
                    document_details = document.get("details", [])
                    if document_details:
                        for detail in document_details:
                            for col_index, milestone in enumerate(all_milestone_columns):
                                value = detail.get(milestone, "")
                                table.setItem(row_index, 5 + col_index, QTableWidgetItem(str(value) if value else ""))

                # Adjust table height to fit rows
                table.resizeRowsToContents()
                total_height = sum(
                    table.rowHeight(row) for row in range(table.rowCount())
                ) + table.horizontalHeader().height()
                table.setFixedHeight(total_height)

                # Add the table to the layout
                self.main_layout.addWidget(table)

    def edit_label(self, event, label):
        """Edit a label when clicked."""
        current_text = label.text().strip().replace("➜ ", "")
        new_name, ok = QInputDialog.getText(self, "Edit Name", "Enter new name:", text=current_text)
        if ok and new_name:
            label.setText(f"    ➜ {new_name}" if "➜" in label.text() else f"<h2>{new_name}</h2>")

    @staticmethod
    def collect_sections(books_data):
        """Collects documents and groups them under sections and subsections."""
        sections = {}
        for book_id, book_data in books_data.items():
            for document in book_data["documents"]:
                section = document["section"]
                subsection = document["subsection"]

                if section not in sections:
                    sections[section] = {}

                if subsection not in sections[section]:
                    sections[section][subsection] = []

                sections[section][subsection].append(document)

        return sections

    def export_html(self):
        QtWidgets.QMessageBox.information(self, "Export HTML", "Export to HTML feature coming soon!")

    def open_in_excel(self):
        QtWidgets.QMessageBox.information(self, "Excel", "Opening in Excel...")

    def open_in_myworkshop(self):
        QtWidgets.QMessageBox.information(self, "MyWorkshop", "Opening in MyWorkshop...")