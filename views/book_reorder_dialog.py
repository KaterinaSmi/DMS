from PyQt6 import QtWidgets, QtCore, QtGui


class BookReorderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, book_name="", books=None):
        super().__init__(parent)
        self.setWindowTitle(f"Reorder Books - {book_name}")
        self.resize(800, 600)

        self.books = books
        self.new_order = []

        self.layout = QtWidgets.QVBoxLayout(self)

        # Instruction Label
        label = QtWidgets.QLabel("Drag and drop books to reorder them.")
        self.layout.addWidget(label)

        # List Widget for displaying books
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.layout.addWidget(self.list_widget)

        # Populate the list with books
        self.populate_list()

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def populate_list(self):
        """Add books to the list widget."""
        for book_name in self.books:
            item = QtWidgets.QListWidgetItem(book_name)
            self.list_widget.addItem(item)

    def accept(self):
        """Capture the new order of books when the dialog is accepted."""
        self.new_order = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        super().accept()