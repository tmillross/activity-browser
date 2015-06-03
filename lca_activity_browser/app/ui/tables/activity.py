# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from ...signals import signals
from ..icons import icons
from brightway2 import Database
from PyQt4 import QtCore, QtGui
import itertools


class ActivityItem(QtGui.QTableWidgetItem):
    def __init__(self, *args, key=None):
        super(ActivityItem, self).__init__(*args)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        self.key = key


class ActivitiesTableWidget(QtGui.QTableWidget):
    COUNT = 100
    COLUMNS = {
        0: "name",
        1: "reference product",
        2: "location",
        3: "unit",
    }

    def __init__(self):
        super(ActivitiesTableWidget, self).__init__()
        self.setDragEnabled(True)
        self.setColumnCount(4)

        self.controller = None

        # Done by tab widget ``MaybeActivitiesTable`` because
        # need to ensure order to get correct row count
        # signals.database_selected.connect(self.sync)
        self.itemDoubleClicked.connect(
            lambda x: signals.activity_selected.emit(x.key)
        )

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.add_activity_action = QtGui.QAction(
            QtGui.QIcon(icons.add), "Add new activity", None
        )
        self.copy_activity_action = QtGui.QAction(
            QtGui.QIcon(icons.copy), "Copy activity", None
        )
        self.addAction(self.add_activity_action)
        self.addAction(self.copy_activity_action)
        # self.add_activity_action.triggered.connect(self.delete_rows)
        self.copy_activity_action.triggered.connect(self.copy_activity)

    def sync(self, name):
        self.clear()
        self.database = Database(name)
        self.database.order_by = 'name'
        self.database.filters = {'type': 'process'}
        self.setRowCount(min(len(self.database), self.COUNT))
        self.setHorizontalHeaderLabels(["Name", "Reference Product", "Location", "Unit"])
        data = itertools.islice(self.database, 0, self.COUNT)
        for row, ds in enumerate(data):
            for col, value in self.COLUMNS.items():
                self.setItem(row, col, ActivityItem(ds.get(value, ''), key=ds.key))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def reset_search(self):
        self.sync(self.database.name)

    def search(self, search_term):
        self.clear()
        search_result = self.database.search(search_term, limit=self.COUNT, **self.database.filters)
        self.setRowCount(len(search_result))
        self.setHorizontalHeaderLabels(["Name", "Reference Product", "Location", "Unit"])
        for row, ds in enumerate(search_result):
            for col, value in self.COLUMNS.items():
                self.setItem(row, col, ActivityItem(ds.get(value, ''), key=ds.key))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def set_controller(self, controller):
        self.controller = controller

    def copy_activity(self, *args):
        if not self.controller:
            return
        print("Copy activity (in table)")
        print(self.currentItem())
        print(self.currentItem().key)
        self.controller.copy_activity(self.currentItem().key)
