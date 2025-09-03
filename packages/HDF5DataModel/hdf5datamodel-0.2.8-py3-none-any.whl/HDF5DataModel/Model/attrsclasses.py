import warnings
from typing import List
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class AttrBase:
    def to_params(self):
        params = []
        for key, value in self.__dict__.items():
            if key == 'start_time':
                dt = datetime.fromtimestamp(value)
                params.append({'name': key, 'type': 'str', 'value': dt.strftime('%d/%m/%y %H:%M:%S.%f')})
            else:
                typ, value = self.get_type_and_cast(value)
                # params.append({'name': key, 'type': 'strict', 'value': value, 'opts': {'type': typ}})  # TODO : comprendre le fonctionnement de ParameterItem et parameterTypes
                params.append({'name': key, 'type': typ, 'value': value})
        return params

    def get_type_and_cast(self, variable):
        if isinstance(variable, str):
            return 'str', variable
        elif isinstance(variable, (int, np.int32, np.int64)):
            return 'int', int(variable)
        elif isinstance(variable, (float, np.float32, np.float64)):
            return 'float', float(variable)
        elif isinstance(variable, list):
            return 'list', variable
        elif isinstance(variable, bool):
            return 'bool', bool(variable)
        else:
            warnings.warn(f"Unsupported type {type(variable)} {variable}, casting to str")
            return 'str', str(variable)

    def set_attrs_from_dict(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key):
                attr_type = type(getattr(self, key))
                if attr_type is list and isinstance(value, np.ndarray):
                    value = value.tolist()
            setattr(self, key, value)


@dataclass
class DatasetAttrs(AttrBase):
    version: str = 'HDF5DataModel 1.0'
    start_time: float = 0.
    experimenter: str = ''
    description: str = ''


@dataclass
class AcquisitionAtrrs(AttrBase):
    start_time: float = 0.
    sample: str = ''
    environment: str = ''
    description: str = ''


@dataclass
class AcqSigAttrs(AttrBase):
    type: str = 'Acquisition attributes'
    start_time: float = 0.
    traces_number: int = 0
    position_interval: float = 0
    position_offset: float = 0
    hardware: str = ''                                    # hardware used to acquire the trace


@dataclass
class GenSigAttrs(AttrBase):
    type: str = 'Generation attributes'
    points_number: int = 0
    central_freq: int = 0
    sampling_freq: int = 0
    duration: float = 0
    transducer: str = ''
    hardware: str = ''
    amplitude: float = 0
    position_x: float = 0
    position_y: float = 0
    position_z: float = 0


@dataclass
class AcqTraceAttrs(AttrBase):
    columns: List[str] = field(default_factory=list)    # list of column names
    units: List[str] = field(default_factory=list)      # list of units for each column
    start_time: float = 0                               # start time of the trace, timestamp in seconds
    duration: float = 0                                 # duration of the trace, seconds
    position_x: float = 0.                              # position of the trace, meters
    position_y: float = 0.                              # position of the trace, meters
    position_z: float = 0.                              # position of the trace, meters
    points_number: int = 0                              # number of points in the trace
    range: float = 0.                                   # range of the trace
    sampling_freq: int = 0                              # sampling frequency of the trace, Hz
    channel: int = 0                                    # acquisition channel of the trace
    index: int = 0                                      # index of the trace in the acquisition signal
    average_number: int = 0                             # number of averaging
    pretrig_duration: float = 0.                        # time between first sample and trig, second
