from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from database.db_methods import get_project_by_name, get_all_project_names
from views.project_window import ProjectWindow

class OpenProjectWindow(QDialog):
    """Dialog for opening an existing project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Project")
        self.setFixedSize(600, 400)
        self.setObjectName("projectWindow")
        self.setModal(True)  #  Ensures the dialog stays on top

        # Layout
        layout = QVBoxLayout()

        # Label
        layout.addWidget(QLabel("🔍 Select a project to open."))

        # Dropdown menu to select project
        self.project_dropdown = QComboBox()
        self.project_dropdown.setObjectName("searchBox")
        self.project_dropdown.setPlaceholderText("Select a project...")
        self.load_projects()
        layout.addWidget(self.project_dropdown)

        # Label to display project details
        self.project_details = QLabel("Project details will appear here")
        self.project_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.project_details)

        # Connect dropdown selection to function
        self.project_dropdown.currentIndexChanged.connect(self.display_project_details)

        #  Initially hidden "Open Project" button
        self.open_btn = QPushButton("Open Project")
        self.open_btn.clicked.connect(self.open_project_window)
        self.open_btn.setVisible(False)  #  Start hidden
        layout.addWidget(self.open_btn)

        # Close Button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def load_stylesheet(self):
        """Loads the QSS stylesheet and applies it to the dialog."""
        try:
            with open("styles.qss", "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Stylesheet not found! Running without styles.")

    def load_projects(self):
        """Load all project names into the drop-down."""
        self.project_map = get_all_project_names()  # Fetch dictionary {name: id}
        if self.project_map:
            self.project_dropdown.addItems(self.project_map.keys())  # Show only names

        else:
            self.project_dropdown.addItem("No projects available")

    def display_project_details(self):
        """Display selected project details."""
        selected_project_name = self.project_dropdown.currentText()
        if selected_project_name and selected_project_name != "No projects available":
            project = get_project_by_name(selected_project_name)  # Fetch project details
            if project:
                self.project_details.setText(f" {project.name}\n {project.description}")
                self.open_btn.setVisible(True)
                self.selected_project_id = project.id  # Store project_id
            else:
                self.project_details.setText(" Project not found.")
                self.open_btn.setVisible(False)
                self.selected_project_id = None
        else:
            self.project_details.setText("Project details will appear here")
            self.open_btn.setVisible(False)
            self.selected_project_id = None


    def open_project_window(self):
        """Opens the project details as a dialog."""
        print(f"🔍 Opening project with ID: {self.selected_project_id}")
        if self.selected_project_id:
            try:
                self.project_dialog = ProjectWindow(self.selected_project_id, self)  #  Parent is self
                self.project_dialog.exec()  #  Use exec() for modal behavior
            except Exception as e:
                print(f"ERROR: Failed to open project window! {e}")
