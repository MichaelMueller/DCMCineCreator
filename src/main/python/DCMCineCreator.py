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


class ValueType(Enum):
    NONE = 0
    STRING = 1
    MULTI_LINE_STRING = 2


class DataObserver:

    def value_added(self, key, new_value):
        pass

    def value_changed(self, key, old_value, new_value):
        pass

    def value_removed(self, key, last_value):
        pass


class Data:
    def __init__(self, namespace=""):
        self.namespace = namespace
        self._observer = []  # type: List[DataObserver]
        self._data = {}

    def set(self, key: str, value):
        key = self.namespace + key
        new_val = key not in self._data.keys()
        old_value = None if new_val else self._data[key]
        self._data[key] = value
        for observer in self._observer:
            observer.value_added(key, value) if new_val else observer.value_changed(self, key, old_value, value)

    def remove(self, key: str):
        if key in self._data.keys():
            last_value = self._data[key]
            del self._data[key]
            for observer in self._observer:
                observer.value_removed(self, key, last_value)

    def has(self, key):
        return key in self._data.keys()

    def get(self, key):
        return self._data[key] if key in self._data.keys() else None

    def keys(self):
        return self._data.keys()

    def key_idx(self, key):
        for idx, curr_key in enumerate(self._data.keys()):
            if curr_key == key:
                return idx
        return -1

    def add_observer(self, observer: DataObserver):
        self._observer.append(observer)


class DataTableWidget(QTableWidget, DataObserver):

    def __init__(self, data: Data, parent: QWidget = None):
        QTableWidget.__init__(self, 0, 3, parent)
        self.setHorizontalHeaderLabels(["Key", "Value", "Help"])
        self.data = data  # type: Data
        self.data.add_observer(self)
        for key in data.keys():
            self.value_added(key, data.get(key))

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
            if self.item(i,0).text() == key:
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
