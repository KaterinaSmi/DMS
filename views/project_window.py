from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, \
    QPushButton, QHBoxLayout, QToolButton, QMenu, QScrollArea, QWidget
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets, QtCore
from database.db_methods import get_project_by_id, get_project_details, get_document_details


class ProjectWindow(QDialog):
    """Dialog displaying project details with product name, sections, and books/documents."""

    def __init__(self, project_id, parent=None):
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
        structured_data = get_project_details(project_id)
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
        self.action_menu.setStyleSheet("QToolButton::menu-indicator { image: none; }")
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

        for section_name, subsections in sections.items():
            # Display section name
            section_label = QLabel(f"<h2>{section_name}</h2>")
            section_label.setStyleSheet("color: #695e93; font-weight: bold;")
            section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(section_label)

            for subsection_name, documents in subsections.items():
                # Display subsection name
                subsection_label = QLabel(f"    ➜ {subsection_name}")
                subsection_label.setStyleSheet("padding-left: 20px; font-weight: bold; color:#695e93;")
                self.main_layout.addWidget(subsection_label)

                # Create Table for Documents
                table = QTableWidget()
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["Document", "Title", "State", "Owner", "Release Date"])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                table.setStyleSheet("background-color: white;")  # White background

                # Populate table with documents
                table.setRowCount(len(documents))
                for row_index, document in enumerate(documents):
                    table.setItem(row_index, 0, QTableWidgetItem(document.get("doc", "")))
                    table.setItem(row_index, 1, QTableWidgetItem(document.get("title", "")))
                    table.setItem(row_index, 2, QTableWidgetItem(document.get("state", "")))
                    table.setItem(row_index, 3, QTableWidgetItem(document.get("owner", "")))
                    table.setItem(row_index, 4, QTableWidgetItem(str(document.get("release_date", ""))))

                # Adjust table height to fit all rows
                table.resizeRowsToContents()
                total_height = sum(
                    table.rowHeight(row) for row in range(table.rowCount())) + table.horizontalHeader().height()
                table.setFixedHeight(total_height)  # Prevent table scroll

                # Add the table to the layout
                self.main_layout.addWidget(table)

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
