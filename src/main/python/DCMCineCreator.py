import os

from PyQt5.QtCore import QRegExp, QFileInfo, QStandardPaths
from PyQt5.QtGui import QRegExpValidator
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QLineEdit, QHBoxLayout, QPushButton, QDialog, QFileDialog, \
    QMessageBox, QLabel, QTableWidget

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
        self._data = []

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
        return self._data.keys().index(key)

    def add_observer(self, observer: DataObserver):
        self._observer.append(observer)


class QDataTable(QTableWidget, DataObserver):

    def __init__(self, data: Data, parent: QWidget = None):
        QTableWidget.__init__(self, len(data.keys), 4, parent)
        self.setHorizontalHeaderLabels(["Key", "Value", "Help", "Error"])
        self.data.add_observer(self)

    def value_added(self, key, new_value):
        pass

    def value_changed(self, key, old_value, new_value):
        pass

    def value_removed(self, key, last_value):
        pass


class DataTreeWidget(QWidget, DataNodeObserver):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=None)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(("Key", "Value"))

        layout = QVBoxLayout()
        layout.addWidget(self.treeWidget)

        self.setLayout(layout)

    def get(self, *keys):
        return None

    def data(self) -> Dict:
        return None

    def set_file_path(self, *keys, value=None, extensions: List[str] = None, must_exist=True, is_dir=False):
        item = self.item(self.treeWidget.invisibleRootItem(), list(keys))
        line_edit = QLineEdit()
        line_edit.setText(value)
        line_edit.setReadOnly(True)
        line_edit.setObjectName(".".join(list(keys)))
        button = QPushButton("Select " + ("directory" if is_dir else "file"))
        button.clicked.connect(lambda: self.filePathButtonClicked(line_edit, value, extensions, must_exist, is_dir))
        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(button)
        widget = QWidget()
        widget.setLayout(layout)
        self.treeWidget.setItemWidget(item, 1, widget)

    def filePathButtonClicked(self, line_edit: QLineEdit, value, extensions: List[str] = None, must_exist=True,
                              is_dir=False):
        if must_exist:
            file_path = QFileDialog.getExistingDirectory(self, "Select directory",
                                                         directory=value) if is_dir else QFileDialog.getOpenFileName(
                self, "Select file", directory=value, filter=extensions)
        else:
            file_path = QFileDialog.getSaveFileName(self, "Select file", value, extensions)
        if file_path and os.path.exists(file_path[0]):
            line_edit.setText(file_path[0])

    def set_string(self, *keys, value, regex=None):
        item = self.item(self.treeWidget.invisibleRootItem(), list(keys))
        line_edit = QLineEdit()
        line_edit.setObjectName(".".join(list(keys)))
        if regex:
            rx = QRegExp(regex)
            validator = QRegExpValidator(rx, self)
            line_edit.setValidator(validator)
        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        widget = QWidget()
        widget.setLayout(layout)
        self.treeWidget.setItemWidget(item, 1, widget)
        return None

    def item(self, item: QTreeWidgetItem, keys: List[str]) -> QTreeWidgetItem:
        curr_key = keys.pop(0)
        curr_item = None
        for idx in range(0, item.childCount()):
            if item.child(idx).text(0) == curr_key:
                curr_item = item.child(idx)
                break
        if not curr_item:
            curr_item = QTreeWidgetItem(item)
            curr_item.setText(0, curr_key)

        if len(keys) > 0:
            return self.item(curr_item, keys)
        else:
            return curr_item


def app_data_path() -> str:
    db_path = QFileInfo(
        QStandardPaths.writableLocation(QStandardPaths.DataLocation) + "/" + ApplicationContext().build_settings[
            'app_name'])
    return db_path.absoluteFilePath()


def convert(data_tree: DataTree):
    # QMessageBox.information(None, "Title", "Message")
    working_dir = data_tree.get("working_dir")


if __name__ == '__main__':
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext

    # datatreewidget
    dtw = DataTreeWidget()
    dtw.set_file_path("working_dir", value=app_data_path(), is_dir=True)
    dtw.set_file_path("video_file", must_exist=True)
    dtw.set_file_path("ref", must_exist=True)
    dtw.treeWidget.expandAll()

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
