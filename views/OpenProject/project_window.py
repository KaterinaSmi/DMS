import csv
import os

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidgetItem, QSizePolicy, \
    QMenu, QScrollArea, QWidget, QInputDialog, QSpacerItem, QHBoxLayout, QSplitter, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from database.db_methods import  get_project_details, get_document_details
from functools import partial
from PyQt6.QtWidgets import QToolButton
from views.drag_and_drop import DraggableFrame, DroppableContainer, DroppableDocumentContainer, DocumentRowWidget, \
    HeaderRowWidget, \
    HeaderRowWidget, DraggableSubsectionFrame


class ProjectWindow(QDialog):
    """Dialog displaying project details with product name, sections, and books/documents."""

    def __init__(self, project_id, selected_documents, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Details")
        self.resize(1000, 800)
        self.setModal(True)
        #track removed sections and subsections
        self.removed_sections = set()
        self.removed_subsections = set()

        self.section_containers = {}  # Add this in __init__ if not already present

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
        self.project_label.setStyleSheet("color: #4D4D4D; margin-left: 370px;")
        self.project_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
                   margin: 10px;
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
        menu.addAction("Add New Section").triggered.connect(self.add_section)
        menu.addAction("Exit").triggered.connect(self.reject)

        self.action_menu.setMenu(menu)
        self.main_layout.addWidget(self.action_menu)

    def display_sections(self, books_data):
        """Displays sections, subsections, and related documents using row-based widgets."""
        sections = self.collect_sections(books_data)
        columns_to_exclude = {"project_id", "relation_id", "document_id", "document_detail_id", "active"}

        for section_name, subsections in sections.items():
            # SECTION SETUP
            section_container = QWidget()
            section_layout = QVBoxLayout(section_container)
            section_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            section_frame = DraggableFrame()
            section_frame.setLayout(section_layout)

            section_label = QLabel(f"<h2>{section_name}</h2>")
            section_label.setStyleSheet("color:#4D4D4D; margin-left: 400px;")
            section_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            #connect the right click to delete
            section_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            section_label.customContextMenuRequested.connect(
                partial(
                    self.show_section_context_menu,
                    section_name=section_name,
                    container_widget=section_frame,  # <-- ВАЖНО: не section_container
                    label_widget=section_label
                )
            )

            section_label.mouseDoubleClickEvent = lambda event, label=section_label: self.edit_label(event, label)
            section_layout.addWidget(section_label)


            subsection_container = DroppableContainer()
            section_layout.addWidget(subsection_container)

            self.section_containers[section_name] = subsection_container

            for subsection_name, documents in subsections.items():
                # SUBSECTION SETUP
                subsection_frame = DraggableFrame()
                subsection_layout = QVBoxLayout(subsection_frame)
                subsection_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

                subsection_label = QLabel(f"    ➜ {subsection_name}")
                subsection_label.setFixedHeight(50)
                subsection_label.setStyleSheet("padding-left: 20px; color: #4D4D4D;")
                subsection_label.mouseDoubleClickEvent = lambda event, label=subsection_label: self.edit_label(event,
                                                                                                               label)
                subsection_layout.addWidget(subsection_label)
                subsection_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                subsection_label.customContextMenuRequested.connect(
                    partial(
                        self.show_subsection_context_menu,
                        section_name=section_name,
                        subsection_name=subsection_name,
                        container_widget=subsection_frame,
                        label_widget=subsection_label
                    )
                )

                # --- DOCUMENT CONTAINER ---
                document_container = DroppableDocumentContainer()
                document_container.layout.setSpacing(0)
                document_container.layout.setContentsMargins(0, 0, 0, 0)


                # --- ADD BUTTON ---
                add_button = QToolButton()
                add_button.setIcon(QIcon.fromTheme("list-add"))
                add_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

                menu = QMenu()

                milestone_action = QAction("Add Milestone", self)
                milestone_action.triggered.connect(partial(self.add_milestone, document_container))
                menu.addAction(milestone_action)

                document_action = QAction("Add Document(s)", self)
                document_action.triggered.connect(partial(self.add_documents, document_container))
                menu.addAction(document_action)
                #add_button.clicked.connect(partial(self.add_milestone, document_container))
                #add_button.setToolTip("Add milestone")
                add_button.setStyleSheet("""
                    QToolButton {
                        margin-left: 10px;
                        border-radius: 5px;
                    }
                    QToolButton::menu-indicator {
                        image: none;  /* Убираем стрелку вниз */
                    }
                """)

                add_button.setMenu(menu)
                add_button.setToolTip("Add milestone or documents")

                subsection_layout.addWidget(add_button)


                subsection_layout.addWidget(document_container)

                # --- FIND ALL MILESTONE COLUMNS ---
                all_milestone_columns = set()
                for document in documents:
                    for detail in document.get("details", []):
                        all_milestone_columns.update(
                            [col for col in detail.keys() if col not in columns_to_exclude]
                        )
                all_milestone_columns = list(all_milestone_columns)

                # --- HEADER ROW ---
                headers = ["Document", "Title", "State", "Owner", "Release Date"] + all_milestone_columns
                header_widget = HeaderRowWidget(headers)
                document_container.layout.addWidget(header_widget)

                # --- DOCUMENT ROWS ---
                for document in documents:
                    doc_widget = DocumentRowWidget(document, all_milestone_columns)
                    doc_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    document_container.layout.addWidget(doc_widget)

                subsection_container.layout.addWidget(subsection_frame)

            self.main_layout.addWidget(section_frame)

    def add_section(self):
        section_name, ok = QInputDialog.getText(self, "New Section Name", "Enter section name:")
        if not ok or not section_name.strip():
            return
        section_name = section_name.strip()

        #Create section container and layout
        section_container = QWidget()
        section_layout = QVBoxLayout(section_container)
        section_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        section_frame = DraggableFrame()
        section_frame.setLayout(section_layout)

        section_label = QLabel(f"<h2>{section_name}</h2>")
        section_label.setStyleSheet("color:#4D4D4D; margin-left: 400px;")
        section_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        section_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        section_label.customContextMenuRequested.connect(
            partial(
                self.show_section_context_menu,
                section_name=section_name,
                container_widget=section_frame,
                label_widget=section_label
            )
        )
        section_label.mouseDoubleClickEvent = lambda event, label=section_label: self.edit_label(event, label)

        section_layout.addWidget(section_label)

        # Empty container for subsections
        subsection_container = DroppableContainer()
        section_layout.addWidget(subsection_container)
        self.section_containers[section_name] = subsection_container

        self.main_layout.addWidget(section_frame)

    def add_subsection(self, section_name):
        subsection_name, ok = QInputDialog.getText(self, "New Subsection Name",
                                                   f"Enter name for new subsection in '{section_name}':")
        if not ok or not subsection_name.strip():
            return
        subsection_name = subsection_name.strip()

        # --- SUBSECTION FRAME ---
        subsection_frame = DraggableFrame()
        subsection_layout = QVBoxLayout(subsection_frame)
        subsection_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- SUBSECTION LABEL ---
        subsection_label = QLabel(f"    ➜ {subsection_name}")
        subsection_label.setFixedHeight(50)
        subsection_label.setStyleSheet("padding-left: 20px; color: #4D4D4D;")
        subsection_label.mouseDoubleClickEvent = lambda event, label=subsection_label: self.edit_label(event, label)
        subsection_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        subsection_label.customContextMenuRequested.connect(
            partial(
                self.show_subsection_context_menu,
                section_name=section_name,
                subsection_name=subsection_name,
                container_widget=subsection_frame,
                label_widget=subsection_label
            )
        )
        subsection_layout.addWidget(subsection_label)

        # --- DOCUMENT CONTAINER ---
        document_container = DroppableDocumentContainer()
        document_container.layout.setSpacing(0)
        document_container.layout.setContentsMargins(0, 0, 0, 0)

        # --- ADD BUTTON ---
        add_button = QToolButton()
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu()
        milestone_action = QAction("Add Milestone", self)
        milestone_action.triggered.connect(partial(self.add_milestone, document_container))
        menu.addAction(milestone_action)

        document_action = QAction("Add Document(s)", self)
        document_action.triggered.connect(partial(self.add_documents, document_container))
        menu.addAction(document_action)

        add_button.setMenu(menu)
        add_button.setToolTip("Add milestone or documents")
        add_button.setStyleSheet("""
            QToolButton {
                margin-left: 10px;
                border-radius: 5px;
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        subsection_layout.addWidget(add_button)
        subsection_layout.addWidget(document_container)

        # --- HEADER ROW ---
        headers = ["Document", "Title", "State", "Owner", "Release Date"]
        header_widget = HeaderRowWidget(headers)
        document_container.layout.addWidget(header_widget)

        # Добавляем весь subsection в соответствующую секцию
        if section_name in self.section_containers:
            self.section_containers[section_name].layout.addWidget(subsection_frame)
        else:
            QMessageBox.warning(self, "Error", f"Section container for '{section_name}' not found.")

    def add_milestone(self, document_container: DroppableDocumentContainer):
        new_key, ok = QInputDialog.getText(self, "Add Milestone", "Enter milestone name:")
        if not ok or not new_key.strip():
            return

        new_key = new_key.strip()

        # 1. Добавим в заголовок
        if isinstance(document_container.layout.itemAt(0).widget(), HeaderRowWidget):
            header_widget: HeaderRowWidget = document_container.layout.itemAt(0).widget()
            header_widget.add_column(new_key)

        # 2. Добавим в каждую строку (DocumentRowWidget)
        for i in range(1, document_container.layout.count()):
            widget = document_container.layout.itemAt(i).widget()
            if isinstance(widget, DocumentRowWidget):
                widget.add_milestone_column(new_key)

    def add_documents(self, document_container: DroppableDocumentContainer):
        files, _ = QFileDialog.getOpenFileNames(self, "Select CSV Documents", "", "CSV Files (*.csv)")
        if not files:
            return

        milestone_columns = []
        if document_container.layout.count() > 0:
            header_widget = document_container.layout.itemAt(0).widget()
            if isinstance(header_widget, HeaderRowWidget):
                milestone_columns = header_widget.get_columns()

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if not isinstance(row, dict) or all(not v.strip() for v in row.values()):
                            continue  # Skip invalid or empty rows

                        document = {
                            "doc": row.get("name", os.path.basename(file_path)),
                            "title": row.get("title", ""),
                            "state": row.get("state", ""),
                            "owner": row.get("owner", ""),
                            "release_date": row.get("releasedate", ""),
                            "details": []
                        }

                        doc_widget = DocumentRowWidget(document, milestone_columns)
                        document_container.layout.addWidget(doc_widget)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read file:\n{file_path}\n\n{e}")

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

    @staticmethod
    def on_section_moved(logical_index, old_visual_index, new_visual_index):
        print(f"Column moved from {old_visual_index} to {new_visual_index}")

    def show_section_context_menu(self, pos, section_name, container_widget, label_widget):
        menu = QMenu(self)

        add_subsection_action = QAction("Add Subsection", self)
        add_subsection_action.triggered.connect(
            lambda: self.add_subsection(section_name)
        )
        menu.addAction(add_subsection_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(
            lambda: self.remove_section(section_name, container_widget)
        )
        menu.addAction(delete_action)

        global_pos = label_widget.mapToGlobal(pos)
        menu.exec(global_pos)

    def show_subsection_context_menu(self, pos, section_name, subsection_name, container_widget, label_widget):
        menu = QMenu(self)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.remove_subsection(section_name, subsection_name, container_widget))
        menu.addAction(delete_action)

        global_pos = label_widget.mapToGlobal(pos)
        menu.exec(global_pos)

    def remove_section(self, section_name, widget):
        self.removed_sections.add(section_name)

        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item and item.widget() == widget:
                self.main_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()
                print(f"Section '{section_name}' removed.")
                break

    def remove_subsection(self, section_name, subsection_name, widget):
        self.removed_subsections.add((section_name, subsection_name))
        widget.setParent(None)
        widget.deleteLater()

    def export_html(self):
        QtWidgets.QMessageBox.information(self, "Export HTML", "Export to HTML feature coming soon!")

    def open_in_excel(self):
        QtWidgets.QMessageBox.information(self, "Excel", "Opening in Excel...")

    def open_in_myworkshop(self):
        QtWidgets.QMessageBox.information(self, "MyWorkshop", "Opening in MyWorkshop...")