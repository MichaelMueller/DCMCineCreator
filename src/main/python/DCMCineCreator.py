import os

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QLineEdit, QHBoxLayout, QPushButton, QDialog, QFileDialog

import sys
from PyQt5 import QtCore, QtWidgets
import backend
from typing import List, Dict, Tuple
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTreeWidget
from PyQt5 import QtCore, QtWidgets


class DataTreeWidget(QWidget, backend.DataTree):

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

    def set_file_path(self, *keys, value, extensions: List[str] = None, must_exist=True):
        item = self.item(self.treeWidget.invisibleRootItem(), list(keys))
        line_edit = QLineEdit()
        line_edit.setReadOnly(True)
        line_edit.setObjectName(".".join(list(keys)))
        button = QPushButton("Select file")
        button.clicked.connect(lambda: self.filePathButtonClicked(line_edit, extensions, must_exist))
        layout = QHBoxLayout()
        layout.addWidget(line_edit)
        layout.addWidget(button)
        widget = QWidget()
        widget.setLayout(layout)
        self.treeWidget.setItemWidget(item, 1, widget)

    def filePathButtonClicked(self, line_edit: QLineEdit, extensions: List[str] = None, must_exist=True):
        if must_exist:
            file_path = QFileDialog.getOpenFileName(None, "Select file", "", extensions)
        else:
            file_path = QFileDialog.getSaveFileName(None, "Select file", "", extensions)
        if os.path.exists(file_path[0]):
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


if __name__ == '__main__':
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    dtw = DataTreeWidget()
    dtw.resize(640, 480)
    d = {'key1': 'value1',
         'key2': 'value2',
         'key3': [1, 2, 3, {1: 3, 7: 9}],
         'key4': object(),
         'key5': {'another key1': 'another value1',
                  'another key2': 'another value2'}}
    # dtw.fillWidget(d)
    dtw.set_string("test", "test", "test", value="test_value")
    dtw.item(dtw.treeWidget.invisibleRootItem(), ["test", "test", "test"]).setExpanded(True)
    dtw.set_file_path("videofile", value="test_value", must_exist=True)
    dtw.treeWidget.expandAll()
    dtw.show()

    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
