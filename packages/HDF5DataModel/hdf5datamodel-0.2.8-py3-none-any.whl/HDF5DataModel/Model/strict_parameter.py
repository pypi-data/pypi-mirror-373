from pyqtgraph.parametertree import parameterTypes, ParameterItem
from PySide6 import QtWidgets


class StrictParameterItem(ParameterItem):
    def __init__(self, param, depth):
        super().__init__(param, depth)


class StrictParameter(parameterTypes.SimpleParameter):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def setValue(self, value, block_signal=None):
        print(self.opts.get('type'), self.opts['type'])
        if self.opts['type'] == int and not isinstance(value, int):
            raise ValueError(f"Invalid value type: expected int, got {type(value).__name__}")
        elif self.opts['type'] == float and not isinstance(value, float):
            raise ValueError(f"Invalid value type: expected float, got {type(value).__name__}")
        elif self.opts['type'] == str and not isinstance(value, str):
            raise ValueError(f"Invalid value type: expected str, got {type(value).__name__}")
        elif self.opts['type'] == list and not isinstance(value, list):
            raise ValueError(f"Invalid value type: expected list, got {type(value).__name__}")
        super().setValue(value, block_signal)

    @property
    def itemClass(self):
        return StrictParameterItem
