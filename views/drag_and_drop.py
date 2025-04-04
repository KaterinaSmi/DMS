from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QApplication, QTableWidget, QAbstractItemView, \
    QTableWidgetItem, QHBoxLayout, QLabel, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt, QMimeData, QDataStream, QIODevice, QByteArray, QPoint
from PyQt6.QtGui import QDrag

#--- SECTION CLASSES ---
#Start dragging the frame
class DraggableFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.setStyleSheet("border: none; margin: 0px; padding: 0px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-dnditemdata", QByteArray())
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)

#Drop the Container with section and its children
class DroppableContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-dnditemdata"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        source = event.source()
        if source and source != self:
            index = self.get_insertion_index(event.position().toPoint())
            self.layout.removeWidget(source)
            self.layout.insertWidget(index, source)

    def get_insertion_index(self, drop_pos):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget.geometry().contains(drop_pos):
                return i
        return self.layout.count()

#--- SUBSECTION CLASSES ---
class DraggableSubsectionFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-subsection", QByteArray())  # <--- другой тип
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)


class DroppableSubsectionContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-subsection"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if source and source != self:
            index = self.get_insertion_index(event.position().toPoint())
            self.layout.removeWidget(source)
            self.layout.insertWidget(index, source)
            event.acceptProposedAction()

    def get_insertion_index(self, drop_pos):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget and widget.geometry().contains(drop_pos):
                return i
        return self.layout.count()

#--- DOCUMENT CLASSES ---
class DraggableDocumentFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-documentrow", QByteArray())  # Custom format
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)


class DroppableDocumentContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-documentrow"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if source and source != self:
            index = self.get_insertion_index(event.position().toPoint())
            self.layout.removeWidget(source)
            self.layout.insertWidget(index, source)
            event.acceptProposedAction()

    def get_insertion_index(self, drop_pos):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget and widget.geometry().contains(drop_pos):
                return i
        return self.layout.count()


class DocumentRowWidget(DraggableDocumentFrame):
    def __init__(self, document, milestone_keys, parent=None):
        super().__init__(parent)
        self.document = document
        self.milestone_keys = milestone_keys
        self.input_fields = {}  # хранение QLineEdit по ключу

        details = document.get("details", [])
        if details:
            first_detail = details[0]
            self.document_id = first_detail.get("document_id")
            self.document_detail_id = first_detail.get("document_detail_id")
        else:
            self.document_id = None
            self.document_detail_id = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.setStyleSheet("""
            QLabel {
                border-right: 1px solid #695e93;
                border-bottom: 1px solid #695e93;
                font-size: 14px;
                background: white;
                color: #333333;
            }
        """)

        def make_label(text, is_wide=False):
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedHeight(40)
            label.setFixedWidth(200 if is_wide else 150)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            return label

        # Static fields
        layout.addWidget(make_label(document.get("doc", ""), is_wide=True))
        layout.addWidget(make_label(document.get("title", ""), is_wide=True))
        layout.addWidget(make_label(document.get("state", "")))
        layout.addWidget(make_label(document.get("owner", "")))
        layout.addWidget(make_label(str(document.get("release_date", ""))))

        # Milestone editable fields
        for milestone in milestone_keys:
            value = ""
            for detail in details:
                if milestone in detail:
                    value = detail[milestone]
                    break
            field = self.make_editable_field(str(value or ""))
            self.input_fields[milestone] = field
            layout.addWidget(field)

    @staticmethod
    def make_editable_field(text):
        field = QLineEdit(text)
        field.setFixedHeight(40)
        field.setFixedWidth(150)
        field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #695e93;
                background-color: white;
                color: #333;
                padding: 5px;
                font-size: 14px;
            }
        """)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return field

    def add_milestone_column(self, key):
        if key in self.input_fields:
            return

        self.milestone_keys.append(key)
        field = self.make_editable_field("")
        self.input_fields[key] = field
        self.layout().addWidget(field)



class HeaderRowWidget(QWidget):
    def __init__(self, headers: list[str], parent=None):
        super().__init__(parent)

        COLUMN_WIDTH = 150
        ROW_HEIGHT = 40

        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        wrapper.setStyleSheet("""
            QLabel {
                background-color: rgba(105, 94, 147, 0.9);
                color: white;
                font-weight: bold;
                border-right: 1px solid white;
                font-size: 14px;
            }
        """)

        for header in headers:
            label = QLabel(header)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedHeight(ROW_HEIGHT)

            if header.lower() in ("title", "document", "name"):
                label.setFixedWidth(200)
            else:
                label.setFixedWidth(150)

            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            layout.addWidget(label)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(wrapper)

        # Match the full row width to content width
        wide_columns = {"document", "title", "name"}
        total_width = 0
        for header in headers:
            if header.lower() in wide_columns:
                total_width += 200
            else:
                total_width += 150
        self.setFixedWidth(total_width)

    def add_column(self, header_name: str):
        label = QLabel(header_name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedHeight(40)
        label.setFixedWidth(150)
        label.setStyleSheet("""
            background-color: rgba(105, 94, 147, 0.9);
            color: white;
            font-weight: bold;
            border-right: 1px solid white;
            font-size: 14px;
        """)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.layout().itemAt(0).widget().layout().addWidget(label)

        current_width = self.width()
        self.setFixedWidth(current_width + 150)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)




