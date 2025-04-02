from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, \
    QPushButton, QHBoxLayout, QToolButton, QMenu, QScrollArea, QWidget, QInputDialog, QSpacerItem
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets, QtCore
from database.db_methods import get_project_by_id, get_project_details, get_document_details
from functools import partial
from views.drag_and_drop import DraggableFrame, DroppableContainer, DraggableDocumentTable


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
        scroll_content = DroppableContainer()  # DroppableContainer is now scrollable content itself
        self.main_layout = scroll_content.layout  # use the layout inside the container

        scroll_area.setWidget(scroll_content)  # scrollable content is now DroppableContainer itself

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
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
            # --- SECTION SETUP ---
            section_container = QWidget()
            section_layout = QVBoxLayout(section_container)
            section_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            # Create section label
            section_label = QLabel(f"<h2>{section_name}</h2>")
            section_label.setStyleSheet("color:#4D4D4D")
            section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            section_label.mouseDoubleClickEvent = lambda event, label=section_label: self.edit_label(event, label)
            section_layout.addWidget(section_label)
            # Subsection container inside section (drag enabled)
            subsection_container = DroppableContainer()
            section_layout.addWidget(subsection_container)

            for subsection_name, documents in subsections.items():
                # --- SUBSECTION SETUP ---
                subsection_widget = QWidget()
                subsection_layout = QVBoxLayout(subsection_widget)
                subsection_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                # Create subsection label
                subsection_label = QLabel(f"    ➜ {subsection_name}")
                subsection_label.setFixedHeight(50)
                subsection_label.setStyleSheet("padding-left: 20px; color: #4D4D4D;")
                subsection_label.mouseDoubleClickEvent = lambda event, label=subsection_label: self.edit_label(event, label)
                subsection_layout.addWidget(subsection_label)

                # Create Table for Documents
                table = DraggableDocumentTable()
                table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                table.setStyleSheet("background-color: white;")
                table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
                table.verticalHeader().setVisible(False)

                add_button = QToolButton()
                add_button.setIcon(QIcon.fromTheme("list-add"))
                add_button.clicked.connect(partial(self.add_milestone, table))
                add_button.setStyleSheet('margin-left: 10px; border-radius: 5px;')
                add_button.setToolTip("Add milestone")
                subsection_layout.addWidget(add_button)
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
                header.sectionMoved.connect(self.on_section_moved)

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
                                item = QTableWidgetItem(str(value) if value else "")
                                item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                table.setItem(row_index, 5 + col_index, item)

                # Adjust table height to fit rows
                table.resizeRowsToContents()
                h_hor_scroll = 0
                if table.columnCount() > 6:
                    h_hor_scroll = table.horizontalScrollBar().height()
                total_height = sum(table.rowHeight(row) for row in range(table.rowCount())) + table.horizontalHeader().height() + h_hor_scroll + 4
                table.setFixedHeight(total_height)
                self.current_table = table

                # Add everything to subsection frame
                subsection_layout.addWidget(table)
                subsection_frame = DraggableFrame()
                subsection_frame.setLayout(subsection_layout)
                subsection_container.layout.addWidget(subsection_frame)

            # Add section to main layout
            section_frame = DraggableFrame()
            section_frame.setLayout(section_layout)
            self.main_layout.addWidget(section_frame)


        #Prevent dropping the table to the bottom if not enougth content
        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def add_milestone(self, table):
        column_name, ok = QInputDialog.getText(self, "Add Milestone", "Enter milestone name:")
        if not ok or not column_name.strip():
            return

        column_name = column_name.strip()

        # 1. Удалим пустую колонку в конце (если она есть)
        last_col = table.columnCount() - 1
        if table.horizontalHeaderItem(last_col) and table.horizontalHeaderItem(last_col).text() == "":
            table.removeColumn(last_col)

        # 2. Добавим новую колонку
        new_col_index = table.columnCount()
        table.insertColumn(new_col_index)
        table.setHorizontalHeaderItem(new_col_index, QTableWidgetItem(column_name))

        for row in range(table.rowCount()):
            item = QTableWidgetItem("")
            item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, new_col_index, item)

        # 3. Добавим снова служебную пустую колонку
        table.insertColumn(new_col_index + 1)
        table.setHorizontalHeaderItem(new_col_index + 1, QTableWidgetItem(""))

        # 4. Обновим размеры
        table.resizeColumnsToContents()


    def edit_label(self, event, label):
        """Edit a label when clicked."""
        current_text = label.text().strip()

        # Remove the arrow only if it exists in the text (for subsections)
        if "➜ " in current_text:
            current_text = current_text.replace("➜ ", "")
        elif "<h2>" in current_text and "</h2>" in current_text:
            # Extracting text between <h2>...</h2> tags
            current_text = current_text.replace("<h2>", "").replace("</h2>", "")

        # Display input dialog and sanitize the input
        new_name, ok = QInputDialog.getText(self, "Edit Name", "Enter new name:", text=current_text)
        if ok and new_name:
            # Remove any leading/trailing whitespaces or newlines
            sanitized_name = new_name.strip().replace('\n', '')

            # Update the label text properly
            if "➜" in label.text():
                label.setText(f"    ➜ {sanitized_name}")
            else:
                label.setText(f"<h2>{sanitized_name}</h2>")

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

    def on_section_moved(self, logical_index, old_visual_index, new_visual_index):
        print(f"Column moved from {old_visual_index} to {new_visual_index}")

    def export_html(self):
        QtWidgets.QMessageBox.information(self, "Export HTML", "Export to HTML feature coming soon!")

    def open_in_excel(self):
        QtWidgets.QMessageBox.information(self, "Excel", "Opening in Excel...")

    def open_in_myworkshop(self):
        QtWidgets.QMessageBox.information(self, "MyWorkshop", "Opening in MyWorkshop...")