from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import Qt, QMimeData, QDataStream, QIODevice, QByteArray, QPoint
from PyQt6.QtGui import QDrag


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

#Subsection Classes
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
        self.layout.setSpacing(5)
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

#Document Classes
class DraggableDocumentFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.setStyleSheet("border: 1px solid #ccc; margin: 2px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-documentdata", QByteArray())
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)


class DroppableDocumentContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-documentdata"):
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

    def get_insertion_index(self, drop_pos: QPoint):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget and widget.geometry().contains(drop_pos):
                return i
        return self.layout.count()

