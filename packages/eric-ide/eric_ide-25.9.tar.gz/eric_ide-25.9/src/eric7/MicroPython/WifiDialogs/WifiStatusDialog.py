# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show the WiFi status of the connected device.
"""

import contextlib

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTreeWidgetItem

from eric7.EricGui import EricPixmapCache
from eric7.SystemUtilities.NetworkUtilities import ipv6AddressScope

from .Ui_WifiStatusDialog import Ui_WifiStatusDialog


class WifiStatusDialog(QDialog, Ui_WifiStatusDialog):
    """
    Class implementing a dialog to show the WiFi status of the connected device.
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
        # clear old data
        self.statusTree.clear()

        # get the status
        try:
            clientStatus, apStatus, overallStatus = self.__mpy.getDevice().getWifiData()
        except Exception as exc:
            self.__mpy.showError("getWifiData()", str(exc))
            return

        # populate overall status
        QTreeWidgetItem(
            self.statusTree,
            [
                self.tr("Active"),
                self.tr("Yes") if overallStatus["active"] else self.tr("No"),
            ],
        )
        with contextlib.suppress(KeyError):
            QTreeWidgetItem(
                self.statusTree, [self.tr("Hostname"), overallStatus["hostname"]]
            )
        with contextlib.suppress(KeyError):
            QTreeWidgetItem(
                self.statusTree, [self.tr("Country"), overallStatus["country"]]
            )
        with contextlib.suppress(KeyError):
            QTreeWidgetItem(
                self.statusTree,
                [self.tr("Preferred IP Version"), str(overallStatus["prefer"])],
            )

        # populate status of client interface
        if clientStatus:
            header = self.__createHeader(self.tr("Client"))
            QTreeWidgetItem(
                header,
                [
                    self.tr("Active"),
                    self.tr("Yes") if clientStatus["active"] else self.tr("No"),
                ],
            )
            if clientStatus["active"]:
                QTreeWidgetItem(
                    header,
                    [
                        self.tr("Connected"),
                        self.tr("Yes") if clientStatus["connected"] else self.tr("No"),
                    ],
                )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(header, [self.tr("Status"), clientStatus["status"]])
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(header, [self.tr("SSID"), clientStatus["essid"]])
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header, [self.tr("Channel"), str(clientStatus["channel"])]
                    )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header, [self.tr("Country"), clientStatus["country"]]
                    )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header,
                        [
                            self.tr("Tx-Power"),
                            self.tr("{0} dBm").format(clientStatus["txpower"]),
                        ],
                    )
                QTreeWidgetItem(header, [self.tr("MAC-Address"), clientStatus["mac"]])

                # IPv4 specific data
                ip4Header = self.__createSubheader(header, self.tr("IPv4"))
                QTreeWidgetItem(
                    ip4Header, [self.tr("Address"), clientStatus["ifconfig"][0]]
                )
                QTreeWidgetItem(
                    ip4Header, [self.tr("Netmask"), clientStatus["ifconfig"][1]]
                )
                QTreeWidgetItem(
                    ip4Header, [self.tr("Gateway"), clientStatus["ifconfig"][2]]
                )
                QTreeWidgetItem(
                    ip4Header, [self.tr("DNS"), clientStatus["ifconfig"][3]]
                )

                # IPv6 specific data
                if clientStatus["ipv6_addr"]:
                    ip6Header = self.__createSubheader(header, self.tr("IPv6"))
                    ip6AddrHeader = self.__createSubheader(
                        ip6Header, self.tr("Addresses"), underlined=False
                    )
                    for addr in sorted(clientStatus["ipv6_addr"]):
                        QTreeWidgetItem(
                            ip6AddrHeader, [addr.lower(), ipv6AddressScope(addr)]
                        )

                # data about the connected access point
                if "ap_ssid" in clientStatus:
                    apHeader = self.__createSubheader(
                        header, self.tr("Connected Access Point")
                    )
                    QTreeWidgetItem(
                        apHeader, [self.tr("Name"), clientStatus["ap_ssid"]]
                    )
                    with contextlib.suppress(KeyError):
                        QTreeWidgetItem(
                            apHeader,
                            [self.tr("Channel"), str(clientStatus["ap_channel"])],
                        )
                    QTreeWidgetItem(
                        apHeader, [self.tr("MAC-Address"), clientStatus["ap_bssid"]]
                    )
                    QTreeWidgetItem(
                        apHeader, [self.tr("RSSI [dBm]"), str(clientStatus["ap_rssi"])]
                    )
                    QTreeWidgetItem(
                        apHeader, [self.tr("Security"), clientStatus["ap_security"]]
                    )
                    with contextlib.suppress(KeyError):
                        QTreeWidgetItem(
                            apHeader, [self.tr("Country"), clientStatus["ap_country"]]
                        )

        # populate status of access point interface
        if apStatus:
            header = self.__createHeader(self.tr("Access Point"))
            QTreeWidgetItem(
                header,
                [
                    self.tr("Active"),
                    self.tr("Yes") if apStatus["active"] else self.tr("No"),
                ],
            )
            if apStatus["active"]:
                QTreeWidgetItem(
                    header,
                    [
                        self.tr("Connected"),
                        self.tr("Yes") if apStatus["connected"] else self.tr("No"),
                    ],
                )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(header, [self.tr("Status"), apStatus["status"]])
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(header, [self.tr("SSID"), apStatus["essid"]])
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header, [self.tr("Security"), apStatus["ap_security"]]
                    )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header, [self.tr("Channel"), str(apStatus["channel"])]
                    )
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(header, [self.tr("Country"), apStatus["country"]])
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        header,
                        [
                            self.tr("Tx-Power"),
                            self.tr("{0} dBm").format(apStatus["txpower"]),
                        ],
                    )
                QTreeWidgetItem(header, [self.tr("MAC-Address"), apStatus["mac"]])

                # IPv4 specific data
                ip4Header = self.__createSubheader(header, self.tr("IPv4"))
                with contextlib.suppress(KeyError):
                    QTreeWidgetItem(
                        ip4Header, [self.tr("Address"), apStatus["ifconfig"][0]]
                    )
                    QTreeWidgetItem(
                        ip4Header, [self.tr("Netmask"), apStatus["ifconfig"][1]]
                    )
                    QTreeWidgetItem(
                        ip4Header, [self.tr("Gateway"), apStatus["ifconfig"][2]]
                    )
                    QTreeWidgetItem(
                        ip4Header, [self.tr("DNS"), apStatus["ifconfig"][3]]
                    )

                # IPv6 specific data
                if clientStatus["ipv6_addr"]:
                    ip6Header = self.__createSubheader(header, self.tr("IPv6"))
                    ip6AddrHeader = self.__createSubheader(
                        ip6Header, self.tr("Addresses"), underlined=False
                    )
                    for addr in sorted(apStatus["ipv6_addr"]):
                        QTreeWidgetItem(
                            ip6AddrHeader, [addr.lower(), ipv6AddressScope(addr)]
                        )

        for col in range(self.statusTree.columnCount()):
            self.statusTree.resizeColumnToContents(col)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Close).setDefault(True)
        self.buttonBox.setFocus(Qt.FocusReason.OtherFocusReason)

    def __createHeader(self, headerText):
        """
        Private method to create a header item.

        @param headerText text for the header item
        @type str
        @return reference to the created header item
        @rtype QTreeWidgetItem
        """
        headerItem = QTreeWidgetItem(self.statusTree, [headerText])
        headerItem.setExpanded(True)
        headerItem.setFirstColumnSpanned(True)

        font = headerItem.font(0)
        font.setBold(True)
        headerItem.setFont(0, font)

        return headerItem

    def __createSubheader(self, parent, text, underlined=True):
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
