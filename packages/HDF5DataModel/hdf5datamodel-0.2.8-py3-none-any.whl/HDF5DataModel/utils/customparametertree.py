from pyqtgraph.parametertree import Parameter, ParameterTree
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QApplication


class CustomParameterTree(ParameterTree):
    right_click = Signal(QPoint)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.right_click.emit(event.position().toPoint())
        else:
            super().mousePressEvent(event)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    tree = CustomParameterTree()
    param = Parameter.create(name='Test', type='group', children=[
        {'name': 'param1', 'type': 'int', 'value': 10},
        {'name': 'param2', 'type': 'float', 'value': 3.14},
        {'name': 'param3', 'type': 'str', 'value': 'Hello'}
    ])
    tree.setParameters(param, showTop=False)
    tree.show()
    sys.exit(app.exec())