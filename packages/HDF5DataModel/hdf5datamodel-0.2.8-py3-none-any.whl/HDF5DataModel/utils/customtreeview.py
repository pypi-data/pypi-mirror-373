from PySide6.QtCore import Qt, QEvent, Signal, QModelIndex
from PySide6.QtWidgets import QTreeView, QAbstractItemView
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import QItemSelectionModel, QItemSelection
import numpy as np


class CustomizedTreeView(QTreeView):
    debug = False
    delete_pressed = Signal()
    escape_pressed = Signal()
    drag_drop = Signal(QStandardItem, int, QStandardItem)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.moving = False
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def selection_changed_tester(self):
        import time
        print(time.time(), 'selection_changed_tester')

    def dragEnterEvent(self, event):
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.source() == self:
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.source() == self:
            target_index = self.indexAt(event.pos())
            source_index = self.currentIndex()
            if target_index.isValid() and target_index != source_index:
                source_level = self.get_item_level(source_index)
                target_level = self.get_item_level(target_index)

                if target_level == source_level - 1 and target_level <= 3:
                    super().dropEvent(event)
                    self.drag_drop.emit(source_index, source_level, target_index)
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:
            # Suppr pressed
            # print('Suppr pressed')
            self.delete_pressed.emit()

        elif event.key() == Qt.Key_Backspace:
            # Back space
            print('Back space pressed => Suppr')
            self.delete_pressed.emit()

        elif event.key() == Qt.Key_Escape:
            # Escape pressed
            print('Escape pressed')
            # self.escape_pressed.emit()
            self.selectionModel().clearSelection()

        else:
            super(QTreeView, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.last_pressed_index = self.indexAt(event.position().toPoint())
            self.moving = True
            if self.debug:
                print('super().mousePressEvent')
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.moving = False
            previous_selection = QItemSelection()
            self.selectionModel().selectionChanged.emit(previous_selection, self.selectionModel().selection())
            if self.selectionModel().selection().indexes():
                self.selectionModel().setCurrentIndex(self.selectionModel().selection().indexes()[-1], QItemSelectionModel.Select)
            if self.debug:
                print('super().mouseReleaseEvent')
            super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MiddleButton):
            super().mouseMoveEvent(event)
            return

        current_index = self.indexAt(event.position().toPoint())
        if not current_index.isValid():
            print('out of range')
            return

        current_row = current_index.row()
        if current_index == self.last_pressed_index:
            if self.debug:
                print('mouseMoveEvent: same item')
            return

        current_parent_index = current_index.parent()

        if not current_parent_index.isValid():
            if self.debug:
                print('current item is a top-level item')
            return

        last_pressed_row = self.last_pressed_index.row()
        last_pressed_parent_index = self.last_pressed_index.parent()

        if last_pressed_parent_index != current_parent_index:
            if self.debug:
                print('you moved outside the current top-level item')
            return

        if current_index != self.last_pressed_index:
            selected_rows = [
                index.row()
                for index in self.selectionModel().selectedRows(current_parent_index.column())
            ]

            newly_selected_rows = [
                row - last_pressed_row + current_row for row in selected_rows
            ]

            self.last_pressed_index = current_index

            self.selectionModel().blockSignals(True)
            for row in selected_rows:
                if row not in newly_selected_rows:
                    self.selectionModel().select(
                        self.model().index(row, 0, current_parent_index),
                        QItemSelectionModel.Deselect
                    )

            for row in newly_selected_rows:
                if row not in selected_rows:
                    self.selectionModel().select(
                        self.model().index(row, 0, current_parent_index),
                        QItemSelectionModel.Select
                    )
            self.selectionModel().blockSignals(False)
            previous_selection = QItemSelection()
            self.selectionModel().selectionChanged.emit(previous_selection, self.selectionModel().selection())

            self.viewport().update()

        if self.debug:
            print('mouseMoveEvent', [
                self.model().itemFromIndex(index).text()
                for index in self.selectionModel().selectedRows()
            ])

    def get_item_level(self, index):
        level = 0
        parent = index.parent()
        while parent.isValid():
            level += 1
            parent = parent.parent()
        return level


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    custom_tree_view = CustomizedTreeView()
    custom_tree_view.debug = False
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(['Files'])
    custom_tree_view.resize(300,1000)


    item_texts = ["Item 1", "Item 2", "Item 3"]
    for item_text in item_texts:
        item = QStandardItem(item_text)
        model.appendRow(item)

        for i in range(1, 10):
            subitem_text = f"{item_text}.{i}"
            subitem = QStandardItem(subitem_text)
            item.appendRow(subitem)

    custom_tree_view.setModel(model)

    custom_tree_view.show()
    sys.exit(app.exec())

