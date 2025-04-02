from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget, QApplication, QTableWidget, QAbstractItemView, \
    QTableWidgetItem
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

#--- DOCUMENT CLASSES ---
class DraggableDocumentTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTableWidget.DragDropMode.DragDrop)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setStyleSheet("QTableWidget::item:selected { background-color: #D0E9FF; }")

    def startDrag(self, supportedActions):
        row = self.currentRow()
        if row == -1:
            return

        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)

        for col in range(self.columnCount()):
            item = self.item(row, col)
            stream.writeQString(item.text() if item else "")

        mime_data.setData("application/x-documentrow", encoded_data)

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-documentrow"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-documentrow"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.source() != self:
            event.ignore()
            return

        source_row = self.currentRow()
        drop_index = self.indexAt(event.position().toPoint())
        drop_row = drop_index.row()

        if source_row == -1:
            event.ignore()
            return

        if drop_row == -1 or drop_row == source_row:
            drop_row = self.rowCount() if drop_row == -1 else drop_row
            event.ignore()
            return

        # Collect data from source row
        row_data = []
        for col in range(self.columnCount()):
            item = self.item(source_row, col)
            row_data.append(item.text() if item else "")

        # Insert at new position
        self.insertRow(drop_row)
        for col, text in enumerate(row_data):
            new_item = QTableWidgetItem(text)
            new_item.setFlags(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            new_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(drop_row, col, new_item)

        # Remove original row
        if source_row > drop_row:
            self.removeRow(source_row + 1)
        else:
            self.removeRow(source_row)

        self.resizeRowsToContents()

        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()
