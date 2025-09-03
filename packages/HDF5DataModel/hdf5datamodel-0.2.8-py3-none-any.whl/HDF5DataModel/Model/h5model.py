import warnings
from PySide6.QtCore import Signal, QObject
from h5py import File
from HDF5DataModel.Model.subclasses import Dataset


class H5DataModel(QObject):
    modelUpdated = Signal()

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.file = None   # ???
        self.datasets = {}

    def add_dataset(self, name):
        self.datasets[name] = Dataset(name)
        return self.datasets[name]

    def to_hdf5_file(self):
        with File(self.file_path, 'w') as f:
            for name, dataset in self.datasets.items():
                dataset.to_hdf5_file(f)

    def get_datasets(self):
        with File(self.file_path, 'r') as f:
            for key in f.keys():
                if f[key].attrs['version'][:-4] == 'HDF5DataModel':
                    dataset = Dataset()
                    dataset.from_h5(f, key)
                    self.datasets[key] = dataset
                else:
                    warnings.warn('version not recognized')


if __name__ == '__main__':
    h5 = H5DataModel(r'C:\Users\devie\Documents\Programmes\HDF5DataModel\test.h5')
    h5.get_datasets()
