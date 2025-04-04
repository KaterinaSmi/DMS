from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidgetItem, QSizePolicy, \
    QToolButton, QMenu, QScrollArea, QWidget, QInputDialog, QSpacerItem, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from PyQt6 import QtWidgets
from database.db_methods import  get_project_details, get_document_details
from functools import partial
from views.drag_and_drop import DraggableFrame, DroppableContainer, DroppableDocumentContainer, DocumentRowWidget, HeaderRowWidget, \
    HeaderRowWidget



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

            for subsection_name, documents in subsections.items():
                # SUBSECTION SETUP
                subsection_widget = QWidget()
                subsection_layout = QVBoxLayout(subsection_widget)
                subsection_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


                subsection_label = QLabel(f"    ➜ {subsection_name}")
                subsection_label.setFixedHeight(50)
                subsection_label.setStyleSheet("padding-left: 20px; color: #4D4D4D;")
                subsection_label.mouseDoubleClickEvent = lambda event, label=subsection_label: self.edit_label(event,
                                                                                                               label)
                subsection_layout.addWidget(subsection_label)
                buttons_layout = QVBoxLayout()

                # --- DOCUMENT CONTAINER ---
                document_container = DroppableDocumentContainer()
                document_container.layout.setSpacing(0)
                document_container.layout.setContentsMargins(0, 0, 0, 0)


                # --- ADD BUTTON ---
                add_button = QToolButton()
                add_button.setIcon(QIcon.fromTheme("list-add"))
                add_button.clicked.connect(partial(self.add_milestone, document_container))
                add_button.setStyleSheet('margin-left: 10px; border-radius: 5px;')
                add_button.setToolTip("Add milestone")
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

                # --- WRAP UP SUBSECTION ---
                subsection_frame = DraggableFrame()
                subsection_frame.setLayout(subsection_layout)
                subsection_container.layout.addWidget(subsection_frame)



            self.main_layout.addWidget(section_frame)

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

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.remove_section(section_name, container_widget))
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