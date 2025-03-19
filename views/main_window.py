from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from views.open_project import OpenProjectWindow
from views.create_project import CreateProjectWindow

class MainWindow(QMainWindow):
    """Main menu with 'Open Project' and 'Create Project' buttons and a theme toggle switch."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileNest - Main Menu")
        self.setObjectName("mainWindow")
        #  Default Theme (Dark Mode)
        self.current_theme = "dark"
        self.apply_stylesheet("styles.qss")

        # Label
        self.label = QLabel("Welcome to FileNest")
        self.label.setStyleSheet(
            "color: white; font-size: 28px; font-weight: bold; background: transparent; border: none;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self.open_project_btn = QPushButton("Open Project")
        self.create_project_btn = QPushButton("Create Project")
        self.exit_btn = QPushButton("Exit")

        #  Toggle Switch for Theme (QCheckBox Styled as a Switch)
        self.theme_toggle = QCheckBox("Dark Mode")  # Default is Dark Mode
        self.theme_toggle.setChecked(False)  # Dark Mode initially
        self.theme_toggle.stateChanged.connect(self.toggle_theme)
        self.theme_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # Set cursor to pointer

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.open_project_btn)
        layout.addWidget(self.create_project_btn)
        layout.addWidget(self.exit_btn)
        #  Add Toggle Switch
        layout.addWidget(self.theme_toggle)
        # Set layout
        central_widget.setLayout(layout)

        # Connect buttons to actions
        self.open_project_btn.clicked.connect(self.open_project)
        self.create_project_btn.clicked.connect(self.create_project)
        self.exit_btn.clicked.connect(self.close_application)

    def apply_stylesheet(self, stylesheet):
        """Loads the given QSS file as the application stylesheet."""
        with open(stylesheet, "r") as file:
            self.setStyleSheet(file.read())

    def toggle_theme(self):
        """Switches between light and dark themes."""
        if self.theme_toggle.isChecked():
            self.apply_stylesheet("styles_light.qss")
            self.theme_toggle.setText("Light Mode")  # Update Label
            self.current_theme = "light"
            self.label.setStyleSheet(
                " color: #695e93; font-size: 28px; font-weight: bold; background: transparent; border: none;")  #  Set Black Text
            self.theme_toggle.setStyleSheet(
                "color: #695e93; font-size: 18px; background: transparent;")  # Set Toggle Text to Black


        else:
            self.apply_stylesheet("styles.qss")
            self.theme_toggle.setText("Dark Mode")  # Update Label
            self.current_theme = "dark"
            self.label.setStyleSheet(
                "color: white; font-size: 28px; font-weight: bold; background: transparent; border: none;")  # Set White Text
            self.theme_toggle.setStyleSheet(
                "color: white; font-size: 18px; background: transparent;")  #  Set Toggle Text to White

    def open_project(self):
        """Opens the 'Open Project' window as a modal dialog."""
        dialog = OpenProjectWindow(self)
        dialog.exec()

    def create_project(self):
        """Opens the 'Create Project' window."""
        dialog = CreateProjectWindow(self)
        dialog.exec()

    def close_application(self):
        """Closes the entire app"""
        self.close()
