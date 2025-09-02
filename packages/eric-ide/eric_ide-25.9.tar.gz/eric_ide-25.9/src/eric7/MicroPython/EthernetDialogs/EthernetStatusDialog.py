# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show Ethernet related status information.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTreeWidgetItem

from eric7.EricGui import EricPixmapCache
from eric7.EricGui.EricOverrideCursor import EricOverrideCursor
from eric7.SystemUtilities.NetworkUtilities import ipv6AddressScope

from .Ui_EthernetStatusDialog import Ui_EthernetStatusDialog


class EthernetStatusDialog(QDialog, Ui_EthernetStatusDialog):
    """
    Class implementing a dialog to show Ethernet related status information.
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

    @pyqtSlot()
    def show(self):
        """
        Public slot to show the dialog and populate the status.
        """
        super().show()

        self.__showStatus()

    @pyqtSlot()
    def __showStatus(self):
        """
        Private slot to show the current WiFi status.
        """
        # clear old data
        self.statusTree.clear()

        # get the status
        with EricOverrideCursor():
            try:
                status, addressInfo = self.__mpy.getDevice().getEthernetStatus()
            except Exception as exc:
                self.__mpy.showError("getEthernetStatus()", str(exc))
                return

        for topic, value in status:
            QTreeWidgetItem(self.statusTree, [topic, str(value)])

        if addressInfo["ipv4"]:
            header = self.__createHeader(self.statusTree, self.tr("IPv4"))
            QTreeWidgetItem(header, [self.tr("Address"), addressInfo["ipv4"][0]])
            QTreeWidgetItem(header, [self.tr("Netmask"), addressInfo["ipv4"][1]])
            QTreeWidgetItem(header, [self.tr("Gateway"), addressInfo["ipv4"][2]])
            QTreeWidgetItem(header, [self.tr("DNS"), addressInfo["ipv4"][3]])

        if addressInfo["ipv6"]:
            header = self.__createHeader(self.statusTree, self.tr("IPv6"))
            addrHeader = self.__createHeader(
                header, self.tr("Addresses"), underlined=False
            )
            for addr in sorted(addressInfo["ipv6"]):
                QTreeWidgetItem(addrHeader, [addr.lower(), ipv6AddressScope(addr)])

        for col in range(self.statusTree.columnCount()):
            self.statusTree.resizeColumnToContents(col)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).setDefault(True)
        self.buttonBox.setFocus(Qt.FocusReason.OtherFocusReason)

    def __createHeader(self, parent, text, underlined=True):
        """
        Private method to create a subheader item.

        @param parent reference to the parent item
        @type QTreeWidgetItem
        @param text text for the header item
        @type str
        @param underlined flag indicating an underlined header (defaults to True)
        @type bool (optional)
        @return reference to the created header item
        @rtype QTreeWidgetItem
        """
        headerItem = QTreeWidgetItem(parent, [text])
        headerItem.setExpanded(True)
        headerItem.setFirstColumnSpanned(True)

        if underlined:
            font = headerItem.font(0)
            font.setUnderline(True)
            headerItem.setFont(0, font)

        return headerItem
