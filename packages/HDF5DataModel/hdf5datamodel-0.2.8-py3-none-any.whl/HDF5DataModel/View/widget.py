from typing import Dict, Optional
import os, re, sys, warnings

import numpy as np
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QHeaderView, QMenu, QInputDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QSplitter
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import Signal, Qt, QItemSelectionModel, QItemSelection

from pyqtgraph.parametertree import Parameter, parameterTypes
from HDF5DataModel.Model.strict_parameter import StrictParameter
from HDF5DataModel.Model.h5model import H5DataModel
from HDF5DataModel.Model.subclasses import Dataset, AcqTrace, AcqSig, Acquisition
from HDF5DataModel.utils.customtreeview import CustomizedTreeView
from HDF5DataModel.utils.customparametertree import CustomParameterTree


class H5Widget(QWidget):
    selectionUpdated = Signal(list)

    def __init__(self):
        super().__init__()
        self.widget = None
        self.treeView = None
        self.model = QStandardItemModel()
        self.selection = None
        self.files: Dict[str, H5DataModel] = {}
        self.load_ui()
        self.setup()
        self.file_dialog = QFileDialog()
        parameterTypes.registerParameterType('strict', StrictParameter)

    def load_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        loader = QUiLoader()
        base_path = os.path.dirname(__file__)
        self.widget = loader.load(os.path.join(base_path, 'widget.ui'), self)
        layout.addWidget(self.widget)

    def setup(self):
        self.widget.paramsWidget = CustomParameterTree()
        self.widget.paramsWidget.right_click.connect(self.handle_parameter_tree_context_menu)

        self.treeView = CustomizedTreeView()
        self.widget.treeLayout.insertWidget(0, self.treeView)
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.handle_context_menu)
        self.treeView.delete_pressed.connect(self.handle_suppr)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.widget.paramsWidget)
        splitter.addWidget(self.treeView)
        self.widget.widgetLayout.insertWidget(0, splitter)
        splitter.setSizes([1, 1])

        self.treeView.setModel(self.model)
        self.selection = self.treeView.selectionModel()

        self.widget.browseButton.clicked.connect(self.browse_clicked)
        self.selection.selectionChanged.connect(self.selection_changed)
        self.widget.paramsWidget.header().setSectionResizeMode(QHeaderView.Interactive)
        self.model.setHorizontalHeaderLabels(['Files'])
        self.widget.exportButton.clicked.connect(self.export_selected_files)
        self.treeView.drag_drop.connect(self.item_dropped)

    def browse_clicked(self):
        self.file_dialog.setNameFilter(
            "All Files (*);;"
            "SEG2 Files (*.seg2 *.sg2);;"
            "SEGY Files (*.sgy *.segy);;"
            "SU Files (*.su);;"
            "SEGD Files (*.segd);;"
            "HDF5 Files (*.h5);;"
            )

        self.file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if self.file_dialog.exec() == QFileDialog.Accepted:
            selected_files = self.file_dialog.selectedFiles()
            self.load_files(selected_files)

    def load_files(self, files: str):
        file_name, datamodel, dataset_name, dataset = self.get_last_selected_dataset()

        for filename in files:
            if filename.endswith('.h5'):
                print(f'Loading {filename}')
                self.load_h5(filename)

            elif filename.endswith('.seg2') or filename.endswith('.sg2') or filename.endswith('.SEG2'):
                if dataset is None:
                    file_name, datamodel, dataset_name, dataset = self.create_file_and_dataset(file_name, datamodel,
                                                                                               dataset_name, dataset)
                acq = Acquisition()
                acq.from_seg2(filename)
                dataset.acquisitions[os.path.basename(filename)] = acq
            else:
                raise ValueError(f"{filename} is not a supported file")
        self.update_tree()

    def create_file_and_dataset(self, file_name=None, datamodel=None, dataset_name=None,  dataset=None):
        # no dataset is currently selected, then create a new one
        if file_name is None:
            # this means no datamodel is currently selected
            file_name = f"H5DataModel_{datetime.now().strftime('%Y%m%d%H%M%S')}.h5"
            datamodel = H5DataModel(file_name)
            self.files[file_name] = datamodel
        if dataset_name is None:
            # this means that a new dataset is needed in the current datamodel
            dataset_name = f"Dataset_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            dataset = Dataset(name=dataset_name, parent=datamodel)
            datamodel.datasets[dataset_name] = dataset
        return file_name, datamodel, dataset_name, dataset,

    def load_h5(self, file):
        h5 = H5DataModel(file)
        h5.get_datasets()
        self.files[os.path.basename(file)] = h5
        self.update_tree()
        self.expand_to_level()

    def update_tree(self):
        expanded_indexes = self.save_expansion_state()
        scroll_position = self.treeView.verticalScrollBar().value()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Files'])

        for file, h5 in self.files.items():
            file_item = QStandardItem(os.path.basename(file))
            self.model.appendRow(file_item)

            for dataset in h5.datasets.keys():
                dataset_item = QStandardItem(dataset)
                file_item.appendRow(dataset_item)

                for acq in h5.datasets[dataset].acquisitions.keys():
                    acq_item = QStandardItem(acq)
                    dataset_item.appendRow(acq_item)

                    for sig in h5.datasets[dataset].acquisitions[acq].acq_sigs.keys():
                        sig_item = QStandardItem(sig)
                        acq_item.appendRow(sig_item)

                        for trace in h5.datasets[dataset].acquisitions[acq].acq_sigs[sig].traces.keys():
                            trace_item = QStandardItem(trace)
                            sig_item.appendRow(trace_item)

                    for gen in h5.datasets[dataset].acquisitions[acq].gen_sigs.keys():
                        gen_item = QStandardItem(gen)
                        acq_item.appendRow(gen_item)

        self.treeView.setModel(self.model)
        self.blockSignals(True)
        self.restore_expansion_state(expanded_indexes)
        self.blockSignals(False)
        QApplication.processEvents()
        self.treeView.verticalScrollBar().setValue(scroll_position)
        self.selection_changed()

    def expand_to_level(self, current_level=0):
        def expand_from_level_recursive(item, current_level):
            if current_level < 3:
                self.treeView.setExpanded(item.index(), True)
            for row in range(item.rowCount()):
                expand_from_level_recursive(item.child(row), current_level + 1)
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            expand_from_level_recursive(item, current_level)

    def update_parameter_tree(self, item):
        """
        Update the parameter tree with the selected item
        :param item: selected item
        """
        if not item:
            return

        try:
            attrs = self.get_attrs(item)
            if not attrs:
                return

            param = Parameter.create(name='File', type='group', children=attrs[0])
            if len(attrs) > 1:
                dataset = Parameter.create(name='Dataset', type='group', children=attrs[1])
                param.addChild(dataset)
                if len(attrs) > 2:
                    acquisition = Parameter.create(name='Acquisition', type='group', children=attrs[2])
                    dataset.addChild(acquisition)
                    if len(attrs) > 3:
                        signal = Parameter.create(name='Signal', type='group', children=attrs[3])
                        acquisition.addChild(signal)

                        sel = QItemSelection()
                        for i in range(item.rowCount()):
                            child_index = item.child(i).index()
                            sel.select(child_index, child_index)
                        self.selection.select(sel, QItemSelectionModel.Select)

                        if len(attrs) > 4:
                            trace = Parameter.create(name='Trace', type='group', children=attrs[4])
                            signal.addChild(trace)

        except (KeyError, TypeError) as err:
            warnings.warn(f"Error getting attributes: {err}")
            return
        scroll_position = self.widget.paramsWidget.verticalScrollBar().value()
        if hasattr(self, 'current_param') and self.current_param is not None:
            self.current_param.sigTreeStateChanged.disconnect(self.update_params)
            self.current_param = None

        self.clear_parameter_tree()

        self.widget.paramsWidget.setParameters(param, showTop=True)
        self.current_param = param
        self.current_param.sigTreeStateChanged.connect(self.update_params)
        self.widget.paramsWidget.header().resizeSection(0, 200)
        self.widget.paramsWidget.verticalScrollBar().setValue(scroll_position)

    def selection_changed(self):
        selected_indexes = self.selection.selectedIndexes()
        if not selected_indexes:
            return

        # Récupérer le dernier élément sélectionné
        last_selected_index = selected_indexes[-1]
        item = self.model.itemFromIndex(last_selected_index)

        if not self.treeView.moving:
            self.update_parameter_tree(item)

        selection = self.get_current_selection()
        self.selectionUpdated.emit(selection)

    def clear_parameter_tree(self):

        root = self.widget.paramsWidget.invisibleRootItem()
        count = root.childCount()
        items_to_delete = []

        for i in range(count):
            item = root.child(i)
            items_to_delete.append(item)

        # Detacher tous les enfants du root
        for item in items_to_delete:
            root.removeChild(item)

            # deconnection des signaux (peuvent empecher la supression)
            try:
                item.sigTreeStateChanged.disconnect()
            except Exception:
                pass
            try:
                item.sigValueChanged.disconnect()
            except Exception:
                pass

        # Forcer suppression des objets
        del items_to_delete

    def get_item_level(self, item):
        level = 0
        while item.parent() is not None:
            level += 1
            item = item.parent()
        return level, item

    def get_index_level(self, index):
        level = 0
        while index.parent().isValid():
            level += 1
            index = index.parent()
        return level, index

    def get_attrs(self, item):
        attrs = []
        #  # Traverse the tree to find the corresponding object in the H5DataModel
        level, root_parent = self.get_item_level(item)
        file_name = root_parent.text()
        if file_name in self.files:
            h5 = self.files[file_name]
        else:
            return None

        h5.file_path = h5.file_path if h5.file_path else 'File not created'

        if level == 0:
            attrs += [[{'name': h5.file_path, 'type': 'str', 'value': h5}]]
        elif level == 1:
            attrs += [[{'name': h5.file_path, 'type': 'str', 'value': h5}], h5.datasets[item.text()].attrs.to_params()]
        elif level == 2:
            attrs += [
                [{'name': h5.file_path, 'type': 'str', 'value': h5}],
                h5.datasets[item.parent().text()].attrs.to_params(),
                h5.datasets[item.parent().text()].acquisitions[item.text()].attrs.to_params()
            ]
        elif level == 3:
            if item.text() in h5.datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs:
                attrs3 = h5.datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs[item.text()].attrs.to_params()
            elif item.text() in h5.datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs:
                attrs3 = h5.datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs[item.text()].attrs.to_params()
            else:
                attrs3 = None
            attrs += [
                [{'name': h5.file_path, 'type': 'str', 'value': h5}],
                h5.datasets[item.parent().parent().text()].attrs.to_params(),
                h5.datasets[item.parent().parent().text()].acquisitions[item.parent().text()].attrs.to_params(),
                attrs3]

        elif level == 4:
            attrs += [
                [{'name': h5.file_path, 'type': 'str', 'value': h5}],
                h5.datasets[item.parent().parent().parent().text()].attrs.to_params(),
                h5.datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].attrs.to_params(),
                h5.datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].acq_sigs[item.parent().text()].attrs.to_params(),
                h5.datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].acq_sigs[item.parent().text()].traces[item.text()].attrs.to_params()
                ]
        return attrs

    def update_params(self, param, changes):
        for param, change, data in changes:
            path = self.get_param_path(param)
            self.update_attr(path, data)

    def get_param_path(self, param):
        path = []
        while param is not None:
            path.insert(0, param.name())
            param = param.parent()
        return path

    def update_attr(self, path, value):
        selection = self.get_current_selection()
        if not selection:
            print("No Selection")
            return

        last_selection = selection[-1]

        h5 = self.files[last_selection[0]]

        if path[-1] == 'start_time':
            try:
                value = datetime.strptime(value, '%d/%m/%y %H:%M:%S.%f').timestamp()
            except ValueError:
                print('Invalid date format')
                return

        dataset = last_selection[1]
        if len(path) == 3:
            setattr(h5.datasets[dataset].attrs, path[-1], value)
        elif len(path) >= 4:
            acquisition = last_selection[2]
            if len(path) == 4:
                setattr(h5.datasets[dataset].acquisitions[acquisition].attrs, path[-1], value)
            elif len(path) >= 5:
                signal = last_selection[3]
                if len(path) == 5:
                    if signal in h5.datasets[dataset].acquisitions[acquisition].acq_sigs:
                        setattr(h5.datasets[dataset].acquisitions[acquisition].acq_sigs[signal].attrs, path[-1], value)
                    elif signal in h5.datasets[dataset].acquisitions[acquisition].gen_sigs:
                        setattr(h5.datasets[dataset].acquisitions[acquisition].gen_sigs[signal].attrs, path[-1], value)
                elif len(path) == 6:
                    trace = last_selection[4]
                    setattr(h5.datasets[dataset].acquisitions[acquisition].acq_sigs[signal].traces[trace].attrs,
                            path[-1], value)

    def add_parameter(self, pos_clicked):
        param_name, ok = QInputDialog.getText(self, "Add Parameter", "Parameter name :")
        if ok and param_name:
            param_value, ok = QInputDialog.getText(self, "Add Parameter", "Parameter value :")
            if ok:
                item = self.widget.paramsWidget.itemAt(pos_clicked)
                if item is None:
                    QMessageBox.warning(self, "Error", "No item at clicked position.")
                    return

                last_selected = self.get_current_selection()[-1]
                level, parent = self.get_item_level(item)
                file_name = last_selected[0]
                h5_file = self.files.get(file_name)

                if level == 1:  # Niveau fichier
                    setattr(h5_file.attrs, param_name, param_value)
                elif level == 2:  # Niveau dataset
                    dataset_name = last_selected[1]
                    setattr(h5_file.datasets[dataset_name].attrs, param_name, param_value)
                elif level == 3:  # Niveau acquisition
                    dataset_name = last_selected[1]
                    acquisition_name = last_selected[2]
                    setattr(h5_file.datasets[dataset_name].acquisitions[acquisition_name].attrs, param_name, param_value)
                elif level == 4:  # Niveau signal
                    dataset_name = last_selected[1]
                    acquisition_name = last_selected[2]
                    signal_name = last_selected[3]
                    if signal_name in h5_file.datasets[dataset_name].acquisitions[acquisition_name].acq_sigs:
                        setattr(h5_file.datasets[dataset_name].acquisitions[acquisition_name].acq_sigs[signal_name].attrs, param_name, param_value)
                    elif signal_name in h5_file.datasets[dataset_name].acquisitions[acquisition_name].gen_sigs:
                        setattr(h5_file.datasets[dataset_name].acquisitions[acquisition_name].gen_sigs[signal_name].attrs, param_name, param_value)
                elif level == 5:  # Niveau trace
                    dataset_name = last_selected[1]
                    acquisition_name = last_selected[2]
                    signal_name = last_selected[3]
                    trace_name = last_selected[4]
                    setattr(h5_file.datasets[dataset_name].acquisitions[acquisition_name].acq_sigs[signal_name].traces[trace_name].attrs, param_name, param_value)
                else:
                    QMessageBox.warning(self, "Error", "Selection level not supported.")
        self.update_tree()

    def get_current_selection(self, order_by_row=True):
        """return the current selection
        for each item selected we return a list with all its parents ordered by depth

        :param order_by_row: if True, the selection is ordered by row number in the TreeView,
            otherwise it is ordered according to the mouse selection order

        """
        selection = []

        selected_indexes = self.treeView.selectionModel().selectedIndexes()

        if order_by_row:
            # re-order the selected indexes as they appear in the tree, using their row numbers
            selected_rows = [index.row() for index in selected_indexes]
            positions = np.argsort(selected_rows)
            selected_indexes = [selected_indexes[i] for i in positions]

        for index in selected_indexes:
            item = self.model.itemFromIndex(index)
            if item is None:
                # ????
                continue

            # item is the deepest item selected, find its parents up to the root level
            current_selection = [item.text()]
            parent = item.parent()
            while parent is not None:
                current_selection.append(parent.text())
                parent = parent.parent()

            # add the selected item and all its parent to the returned selection
            selection.append(current_selection[::-1])

        return selection

    def get_last_selected_dataset(self) \
            -> (Optional[str],
                Optional[H5DataModel],
                Optional[str],
                Optional[Dataset]):
        """
        to find the dataset of the last clicked item in the treeview
        :return file_name: str or None, name of the datamodel in self.files
        :return datamodel: H5DataModel or None, the datamodel that was most recently selected
        :return dataset_name: str or None, the name of the dataset in self.files[file_name].datasets
        :return dataset: Dataset or None, the dataset that was most recently selected
        """
        data_selection = self.get_current_selection(order_by_row=False)

        file_name: Optional[str] = None
        datamodel: Optional[H5DataModel] = None

        dataset_name: Optional[str] = None
        dataset: Optional[Dataset] = None

        for item in data_selection[::-1]:
            file_name = item[0]
            datamodel = self.files[file_name]

            if len(item) >= 2:
                dataset_name = item[1]

                dataset = datamodel.datasets[dataset_name]
                break

        return file_name, datamodel, dataset_name, dataset

    def get_last_selected_trace(self) -> Optional[AcqTrace]:
        """
        to find the AcqTrace that has most recently been selected in the TreeView
        :return acq_trace: the last selected acquisition_trace or None
        """
        data_selection = self.get_current_selection(order_by_row=False)

        acq_trace_name = None
        acq_trace = None

        for item in data_selection[::-1]:
            if len(item) == 5:
                (file_name, dataset_name,
                    acq_name, sig_name,
                    acq_trace_name) = item

                # first trace found (starting from the end of the selection list)
                acq_trace: AcqTrace = self \
                    .files[file_name] \
                    .datasets[dataset_name] \
                    .acquisitions[acq_name] \
                    .acq_sigs[sig_name] \
                    .traces[acq_trace_name]
                break

        return acq_trace_name, acq_trace

    def get_last_selected_trace_metadata_names(self, scalar_only: bool=False):
        """
        Collect the names of the metadata names
        available for the last traces selected in the browser
        """
        metadata_names = []

        acq_trace_name, acq_trace = self.get_last_selected_trace()

        if acq_trace is None:
            # No traces were found in this selection
            return metadata_names

        for key, val in acq_trace.attrs.__dict__.items():
            if scalar_only:
                if hasattr(val, "__iter__"):
                    # this is not a scalar value
                    continue
                else:
                    metadata_names.append(key)

        return metadata_names

    def export_selected_files(self):
        """
        Save the selection to an existing directory in a new HDF5 file
        """
        selection = self.get_current_selection()
        if not selection:
            return

        files = []
        for sel in selection:
            if sel[0] not in files:
                files.append(sel[0])

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        if file_dialog.exec() == QFileDialog.Accepted:
            directory = os.path.normpath(file_dialog.selectedFiles()[0])
            for file in files:
                h5 = self.files[file]
                file = re.sub(r'[<>:"/\\|?*]', '_', file)  # ???
                if not file.endswith('.h5'):
                    file += '.h5'
                file_path = os.path.join(directory, file)

                if os.path.exists(file_path):
                    reply = QMessageBox.question(self, 'Confirmation',
                                                 f'Overwrite file?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                h5.file_path = file_path
                h5.to_hdf5_file()
        self.selection_changed()

    def handle_parameter_tree_context_menu(self, pos):
        menu = QMenu(self.widget.paramsWidget)
        add_param_action = QAction("Add Parameter", menu)
        menu.addAction(add_param_action)
        add_param_action.triggered.connect(lambda: self.add_parameter(pos))

        pos_clicked = self.widget.paramsWidget.mapToGlobal(pos)
        menu.exec(pos_clicked)

    def handle_context_menu(self, pos):
        """
        Manage the right click menu
        :param pos:
        """

        menu = QMenu(parent=self.treeView)

        # item = self.treeView.itemAt(pos)
        # index = item.index()
        index = self.treeView.indexAt(pos)

        expand_all_action = QAction("Expand all", menu)
        menu.addAction(expand_all_action)
        expand_all_action.triggered.connect(self.expand_all)

        collapse_all_action = QAction("Collapse all", menu)
        menu.addAction(collapse_all_action)
        collapse_all_action.triggered.connect(self.collapse_all)

        if not index.isValid():
            add_file_action = QAction("Add Empty File", menu)
            menu.addAction(add_file_action)
            add_file_action.triggered.connect(self.add_empty_file)

        # Rename a parent item
        if index.isValid():
            rename_action = QAction("Rename Item...", menu)
            menu.addAction(rename_action)
            rename_action.triggered.connect(lambda: self.rename_index(index))

        # Remove a child or parent item
        if index.isValid():
            # delete only the clicked item
            remove_action = QAction(f"Remove {index.data()}", menu)
            menu.addAction(remove_action)
            remove_action.triggered.connect(lambda: self.remove_index(index))

        if index.isValid():
            # verify that this is an AcqSig

            level, parent = self.get_index_level(index)

            if level == 3:
                # remove the signal
                if index.data() in self.files[parent.data()]\
                        .datasets[index.parent().parent().data()]\
                        .acquisitions[index.parent().data()].acq_sigs:
                    # AcqSignal

                    saveas_action = QAction("Save As...", menu)
                    menu.addAction(saveas_action)
                    saveas_action.triggered.connect(lambda: self.saveas_acqindex(index))

        pos_clicked = self.treeView.mapToGlobal(pos)

        # Show the menu
        menu.exec(pos_clicked)

    def remove_index(self, index, update=True):
        item = self.model.itemFromIndex(index)
        level, parent = self.get_item_level(item)
        if level == 0:
            # remove the top level item
            self.files.pop(item.text())
        elif level == 1:
            # remove the dataset
            self.files[parent.text()].datasets.pop(item.text())
        elif level == 2:
            # remove the acquisition
            self.files[parent.text()].datasets[item.parent().text()].acquisitions.pop(item.text())
        elif level == 3:
            # remove the signal
            if item.text() in self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs:
                self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs.pop(item.text())
            elif item.text() in self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs:
                self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs.pop(item.text())
        elif level == 4:
            # remove the trace
            self.files[parent.text()].datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].acq_sigs[item.parent().text()].traces.pop(item.text())
        if update:
            self.update_tree()

    def rename_index(self, index):
        self.blockSignals(True)
        item = self.model.itemFromIndex(index)
        level, parent = self.get_item_level(item)
        new_name, ok = QInputDialog.getText(self, 'Rename item', 'New name:')
        if not ok:
            return
        if level == 0:
            # remove the top level item
            self.files[new_name] = self.files.pop(item.text())
        elif level == 1:
            # remove the dataset
            self.files[parent.text()].datasets[new_name] = self.files[parent.text()].datasets.pop(item.text())
        elif level == 2:
            # remove the acquisition
            self.files[parent.text()].datasets[item.parent().text()].acquisitions[new_name] = self.files[parent.text()].datasets[item.parent().text()].acquisitions.pop(item.text())
        elif level == 3:
            # remove the signal
            if item.text() in self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs:
                self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs[new_name] = self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].acq_sigs.pop(item.text())
            elif item.text() in self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs:
                self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs[new_name] = self.files[parent.text()].datasets[item.parent().parent().text()].acquisitions[item.parent().text()].gen_sigs.pop(item.text())
        elif level == 4:
            # remove the trace
            self.files[parent.text()].datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].acq_sigs[item.parent().text()].traces[new_name] = self.files[parent.text()].datasets[item.parent().parent().parent().text()].acquisitions[item.parent().parent().text()].acq_sigs[item.parent().text()].traces.pop(item.text())

        self.selection.clearSelection()
        self.update_tree()
        self.blockSignals(False)

    def add_empty_file(self):
        """
        Add an empty file to the model
        """
        file_name, ok = QInputDialog.getText(self, 'Add Empty File', 'File name:')
        if not ok or not file_name:
            return

        if file_name in self.files:
            QMessageBox.warning(self, "Error", f"File {file_name} already exists.")
            return

        # create an empty H5DataModel
        h5 = H5DataModel(file_name)
        self.files[file_name] = h5
        self.update_tree()

    def saveas_acqindex(self, index):
        level, parent = self.get_index_level(index)
        if level != 3:
            return

        acq_sigs = self.files[parent.data()]\
            .datasets[index.parent().parent().data()]\
            .acquisitions[index.parent().data()].acq_sigs

        if index.data() not in acq_sigs:
            return

        # the acquisition signal to save
        acq_sig: AcqSig = acq_sigs[index.data()]

        # open a file dialog to save the acquisition signal
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("SEG2 Files (*.seg2 *.sg2);;")

        #
        if file_dialog.exec() == QFileDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
            if not filename.endswith(('.seg2', ".sg2")):
                raise ValueError(f"File {filename} is not a SEG2 file")

            # save the acquisition signal to the file
            acq_sig.to_seg2(filename=filename)


    def item_dropped(self, index, level, target):
        """
        Handle the drop event
        :param index: index of item to be dropped
        :param level: level of the item
        :param target: target index
        """
        self.selection.selectionChanged.disconnect(self.selection_changed)
        if level == 1:
            # remove the dataset
            self.files[target.data()].datasets[index.data()] = self.files[index.parent().data()].datasets.pop(index.data())
        elif level == 2:
            # remove the acquisition
            self.files[target.parent().data()].datasets[target.data()].acquisitions[index.data()] = self.files[index.parent().parent().data()].datasets[index.parent().data()].acquisitions.pop(index.data())
        elif level == 3:
            # remove the signal
            if index.data() in self.files[index.parent().parent().parent().data()].datasets[index.parent().parent().data()].acquisitions[index.parent().data()].acq_sigs:
                self.files[target.parent().parent().data()].datasets[target.parent().data()].acquisitions[target.data()].acq_sigs[index.data()] = self.files[index.parent().parent().parent().data()].datasets[index.parent().parent().data()].acquisitions[index.parent().data()].acq_sigs.pop(index.data())
            elif index.data() in self.files[index.parent().parent().parent().data()].datasets[index.parent().parent().data()].acquisitions[index.parent().data()].gen_sigs:
                self.files[target.parent().parent().data()].datasets[target.parent().data()].acquisitions[target.data()].gen_sigs[index.data()] = self.files[index.parent().parent().parent().data()].datasets[index.parent().parent().data()].acquisitions[index.parent().data()].gen_sigs.pop(index.data())

        self.treeView.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.treeView.setCurrentIndex(index)
        self.update_tree()
        self.selection.selectionChanged.connect(self.selection_changed)

    def find_index_by_name(self, name):
        """
        Find the index of an item by its name recursively
        :param name: name of the item to find
        :return: index of the item or None if not found
        """
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.text() == name:
                return item.index()
            for child_row in range(item.rowCount()):
                child_item = item.child(child_row)
                if child_item.text() == name:
                    return child_item.index()
                for grandchild_row in range(child_item.rowCount()):
                    grandchild_item = child_item.child(grandchild_row)
                    if grandchild_item.text() == name:
                        return grandchild_item.index()
                    for great_grandchild_row in range(grandchild_item.rowCount()):
                        great_grandchild_item = grandchild_item.child(great_grandchild_row)
                        if great_grandchild_item.text() == name:
                            return great_grandchild_item.index()
        return None

    def collapse_all(self):
        self.treeView.collapseAll()

    def expand_all(self):
        self.treeView.expandAll()

    def select_all(self):
        """
        Select all items
        """
        self.blockSignals(True)
        try:
            for item, parentitem in self.items():
                item.setSelected(True)

        finally:
            self.blockSignals(False)

        self.selection_changed(force=True)

    def deselect_all(self):

        self.blockSignals(True)
        try:
            for item in self.treeView.selectedItems():
                item.setSelected(False)
        finally:
            self.blockSignals(False)

        self.selection_changed()

    def handle_suppr(self):
        """
        Handle the delete key
        """
        selected_indexes = self.selection.selectedIndexes()
        if not selected_indexes:
            return
        reply = QMessageBox.question(
            self,
            "Suppression confirmation",
            f"Are you sure?\nDeleting {[x.data() for x in selected_indexes]} ?.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.blockSignals(True)
            for index in selected_indexes:
                self.remove_index(index, update=False)
            self.blockSignals(False)
            self.update_tree()

    def save_expansion_state(self):
        expanded_paths = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            self.save_expansion_state_recursive(item, expanded_paths, [])
        return expanded_paths

    def save_expansion_state_recursive(self, item, expanded_paths, current_path):
        current_path.append(item.text())
        if self.treeView.isExpanded(item.index()):
            expanded_paths.append(list(current_path))
        for row in range(item.rowCount()):
            self.save_expansion_state_recursive(item.child(row), expanded_paths, current_path)
        current_path.pop()

    def restore_expansion_state(self, expanded_paths):
        for path in expanded_paths:
            for row in range(self.model.rowCount()):
                root_item = self.model.item(row)
                if root_item.text() == path[0]:  # Trouver le bon élément racine
                    self.restore_expansion_state_recursive(root_item, path[1:])
                    break

    def restore_expansion_state_recursive(self, parent_item, path):
        if not path:
            return
        self.treeView.setExpanded(parent_item.index(), True)
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            if child_item.text() == path[0]:
                if len(path) == 1:
                    self.treeView.setExpanded(child_item.index(), True)
                else:
                    self.restore_expansion_state_recursive(child_item, path[1:])


if __name__ == '__main__':
    app = QApplication()
    widget = H5Widget()
    widget.resize(400, 600)
    widget.move(300, 300)
    widget.show()
    sys.exit(app.exec())
