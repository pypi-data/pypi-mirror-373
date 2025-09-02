# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show Bluetooth related status information.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTreeWidgetItem

from eric7.EricGui import EricPixmapCache

from .Ui_BluetoothStatusDialog import Ui_BluetoothStatusDialog


class BluetoothStatusDialog(QDialog, Ui_BluetoothStatusDialog):
    """
    Class implementing a dialog to show Bluetooth related status information.
    """

    def __init__(self, microPython, parent=None):
        """
        Constructor

        @param microPython reference to the MicroPython widget
        @type MicroPythonWidget
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.Window)

        self.statusTree.setColumnCount(2)

        self.refreshButton.setIcon(EricPixmapCache.getIcon("reload"))
        self.refreshButton.clicked.connect(self.__showStatus)

        self.__mpy = microPython

        self.__showStatus()

    @pyqtSlot()
    def __showStatus(self):
        """
        Private slot to show the current WiFi status.
        """
        self.statusTree.clear()

        try:
            status = self.__mpy.getDevice().getBluetoothStatus()
            # status is a list of user labels and associated values
        except Exception as exc:
            self.__mpy.showError("getBluetoothStatus()", str(exc))
            return

        for topic, value in status:
            QTreeWidgetItem(self.statusTree, [topic, str(value)])

        for col in range(self.statusTree.columnCount()):
            self.statusTree.resizeColumnToContents(col)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).setDefault(True)
        self.buttonBox.setFocus(Qt.FocusReason.OtherFocusReason)
