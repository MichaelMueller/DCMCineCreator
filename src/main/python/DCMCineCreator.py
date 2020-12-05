import os

from PyQt5.QtCore import QRegExp, QFileInfo, QStandardPaths
from PyQt5.QtGui import QRegExpValidator
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QLineEdit, QHBoxLayout, QPushButton, QDialog, QFileDialog, \
    QMessageBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView

import sys
from PyQt5 import QtCore, QtWidgets
from typing import List, Dict, Tuple
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTreeWidget
from PyQt5 import QtCore, QtWidgets

import abc
from typing import List, Dict, Tuple
from enum import Enum


class Descriptor:

    def __init__(self, mutable=True):
        self._mutable = mutable

    def mutable(self):
        return self._mutable


class PropertyType(Enum):
    NONE = 0
    STRING = 1
    MULTI_LINE_STRING = 2
    BOOL = 3
    INT = 4
    FLOAT = 5


class Property(Descriptor):

    def __init__(self, type: PropertyType, mutable=True):
        super(Descriptor, self).__init__(mutable)
        self._type = type

    def type(self):
        return self._type


class ArrayDescriptor(Descriptor):

    def __init__(self, mutable=True):
        super(Descriptor, self).__init__(mutable)


class DictDescriptor(ArrayDescriptor):

    def __init__(self, mutable=True):
        super(Descriptor, self).__init__(mutable)
        self._properties = {}  # type: Dict[Descriptor]

    def add_descriptor(self, key, descriptor: Descriptor):
        self._properties[key] = descriptor

    def keys(self):
        return self._properties.keys()

    def descriptor(self, key):
        return self._properties[key]


class ListDescriptor(ArrayDescriptor):

    def __init__(self, element_descriptor: Descriptor, mutable=True):
        super(Descriptor, self).__init__(mutable)
        self._element_descriptor = element_descriptor

    def is_table(self):
        return isinstance(self._element_descriptor, DictDescriptor)

    def descriptor(self):
        return self._element_descriptor


class DataTableWidget(QTableWidget):

    def __init__(self, parent: QWidget = None):
        super(QTableWidget, self).__init__(self, 0, 3, parent)
        self._list = None  # type: List
        self._list_descriptor = None  # type: ListDescriptor
        self._dict = None  # type: Dict
        self._dict_descriptor = None  # type: DictDescriptor

    def set_list(self, _list: List, list_descriptor: ListDescriptor):
        self._dict = None
        self._dict_descriptor = None
        self._list = _list
        self._list_descriptor = list_descriptor
        self.data_changed()

    def set_dict(self, _dict: Dict, dict_descriptor: DictDescriptor):

        self._list = None
        self._list_descriptor = None
        self._dict = _dict
        self._dict_descriptor = dict_descriptor
        self.data_changed()

    def data_changed(self):
        # header
        if self._list_descriptor and self._list_descriptor.is_table():
            self.setHorizontalHeaderLabels(self._list_descriptor.descriptor().keys())
        else:
            self.setHorizontalHeader(["Key", "Value"])
            size = len(self._list) if self._list else len(self._dict.keys())
            self.setRowCount(size + 1)
            if self._list:
                for idx, item in enumerate(self._list):
                    self.setItem(idx, 0, QTableWidgetItem(str(idx+1)))
                    self.setItem(idx, 1, QTableWidgetItem(str(item)))

            if self._dict_descriptor:
                for idx, item in enumerate(self._list):
                    self.setItem(idx, 0, QTableWidgetItem(str(idx+1)))
                    self.setItem(idx, 1, QTableWidgetItem(str(item)))


        # data

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def value_added(self, key, new_value):
        self.value_changed(key, None, new_value)

    def rchop(self, s, suffix):
        if suffix and s.endswith(suffix):
            return s[:-len(suffix)]
        return s

    def value_changed(self, key, old_value, new_value):

        if key.endswith(".error"):
            idx = self.idx_for_key(self.rchop(key, ".error"))
            col_idx = 3
        elif key.endswith(".help"):
            idx = self.idx_for_key(self.rchop(key, ".help"))
            col_idx = 2
        else:
            idx = self.idx_for_key(key)
            col_idx = 1
        self.setItem(idx, col_idx, QTableWidgetItem(new_value))

    def value_removed(self, key, last_value):
        idx = self.data.key_idx(key)
        self.removeRow(idx)

    def idx_for_key(self, key, create=False):
        for i in range(0, self.rowCount()):
            if self.item(i, 0).text() == key:
                return i
        idx = self.rowCount()
        self.setRowCount(idx + 1)
        self.setItem(idx, 0, QTableWidgetItem(key))
        return idx


def app_data_path() -> str:
    db_path = QFileInfo(
        QStandardPaths.writableLocation(QStandardPaths.DataLocation) + "/" + ApplicationContext().build_settings[
            'app_name'])
    return db_path.absoluteFilePath()


def convert(data: Data):
    # QMessageBox.information(None, "Title", "Message")
    working_dir = data.get("working_dir")


if __name__ == '__main__':
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext

    # data
    data = Data()
    data.set("working_dir", value=app_data_path())
    data.set("working_dir.help", "The actual working dir (defaults to the AppData path")
    data.set("video_file", None)
    data.set("ref_dcm_file", None)

    # datatreewidget
    dtw = DataTableWidget(data)

    # convert button
    convertButton = QPushButton("start conversion")
    convertButton.clicked.connect(lambda: convert())

    # build main layout
    layout = QVBoxLayout()
    layout.addWidget(dtw)
    layout.addWidget(convertButton)

    # build main widget
    main_widget = QWidget()
    main_widget.setLayout(layout)

    # build window title
    app_context = ApplicationContext()
    version = app_context.build_settings['version']
    app_name = app_context.build_settings['app_name']
    window_title = app_name + " v" + version

    # build main window
    mainWindow = QMainWindow()
    mainWindow.resize(640, 480)
    mainWindow.show()
    mainWindow.setWindowTitle(window_title)
    mainWindow.setCentralWidget(main_widget)
    mainWindow.resize(800, 600)

    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
