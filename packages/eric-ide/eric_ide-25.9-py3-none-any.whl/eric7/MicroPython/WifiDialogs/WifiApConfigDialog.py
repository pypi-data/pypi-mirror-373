# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to configure the Access Point interface.
"""

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7 import Preferences

from .Ui_WifiApConfigDialog import Ui_WifiApConfigDialog


class WifiApConfigDialog(QDialog, Ui_WifiApConfigDialog):
    """
    Class implementing a dialog to configure the Access Point interface.
    """

    def __init__(self, withIP, securityModes, parent=None):
        """
        Constructor

        @param withIP flag indicating to ask the user for an IP configuration
        @type bool
        @param securityModes list of supported security modes
        @type list of str
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        self.__securityMapping = {
            "SEC_DPP": "DPP",
            "SEC_OPEN": self.tr("Open"),
            "SEC_OWE": "OWE",
            "SEC_WAPI": "WAPI",
            "SEC_WEP": "WEP",
            "SEC_WPA": "WPA",
            "SEC_WPA_WPA2": "WPA/WPA2",
            "SEC_WPA2": "WPA2",
            "SEC_WPA2_ENT": "WPA2 Enterprise",
            "SEC_WPA2_WPA3": "WPA2/WPA3",
            "SEC_WPA2_WPA3_ENT": "WPA2/WPA3 Enterprise",
            "SEC_WPA3": "WPA3",
            "SEC_WPA3_ENT": "WPA3 Enterprise",
            "SEC_WPA3_ENT_192": "WPA3 Enterprise (192-bit)",
            "SEC_WPA3_EXT_PSK": "WPA3 Extended",
            "SEC_WPA3_EXT_PSK_MIXED_MODE": "WPA3 Extended, Mixed Mode",
        }

        # populate the WiFi security mode combo box
        for securityMode in sorted(securityModes):
            try:
                self.apSecurityComboBox.addItem(
                    self.__securityMapping[securityMode], securityMode
                )
            except KeyError:
                self.apSecurityComboBox.addItem(securityMode, securityMode)
        self.apSecurityComboBox.model().sort(0)

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        # populate the WiFi fields with data saved to the preferences
        self.apSsidEdit.setText(Preferences.getMicroPython("WifiApName"))
        self.apPasswordEdit.setText(Preferences.getMicroPython("WifiApPassword"))
        index = self.apSecurityComboBox.findData(
            Preferences.getMicroPython("WifiApAuthMode")
        )
        if index == -1:
            index = self.apSecurityComboBox.findData("SEC_WPA_WPA2")
            # default it to WPA/WPA2 in case of an issue
        self.apSecurityComboBox.setCurrentIndex(index)
        self.hostnameEdit.setText(Preferences.getMicroPython("WifiApHostname"))

        self.__withIP = withIP

        self.ipv4GroupBox.setVisible(withIP)
        if withIP:
            # populate the IPv4 configuration with data saved to the preferences
            self.addressEdit.setText(Preferences.getMicroPython("WifiApAddress"))
            self.netmaskEdit.setText(Preferences.getMicroPython("WifiApNetmask"))
            self.gatewayEdit.setText(Preferences.getMicroPython("WifiApGateway"))
            self.dnsEdit.setText(Preferences.getMicroPython("WifiApDNS"))

            # connect the IPv4 fields
            self.addressEdit.addressChanged.connect(self.__updateOk)
            self.netmaskEdit.addressChanged.connect(self.__updateOk)
            self.gatewayEdit.addressChanged.connect(self.__updateOk)
            self.dnsEdit.addressChanged.connect(self.__updateOk)

        # connect the WiFi fields
        self.apSsidEdit.textChanged.connect(self.__updateOk)
        self.apPasswordEdit.textChanged.connect(self.__updateOk)
        self.apSecurityComboBox.currentIndexChanged.connect(self.__updateOk)

        self.__updateOk()

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    @pyqtSlot()
    def __updateOk(self):
        """
        Private method to update the enabled state of the OK button.
        """
        enable = bool(self.apSsidEdit.text())
        if self.apSecurityComboBox.currentData() != "SEC_OPEN":
            # security needs a password
            enable &= bool(self.apPasswordEdit.text())
        if self.__withIP:
            enable &= (
                self.addressEdit.hasAcceptableInput()
                and self.netmaskEdit.hasAcceptableInput()
                and self.gatewayEdit.hasAcceptableInput()
                and self.dnsEdit.hasAcceptableInput()
            )

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    @pyqtSlot()
    def accept(self):
        """
        Public slot accepting the dialog.
        """
        if self.rememberCheckBox.isChecked():
            Preferences.setMicroPython("WifiApName", self.apSsidEdit.text())
            Preferences.setMicroPython("WifiApPassword", self.apPasswordEdit.text())
            Preferences.setMicroPython(
                "WifiApAuthMode", self.apSecurityComboBox.currentData()
            )
            Preferences.setMicroPython("WifiApHostname", self.hostnameEdit.text())
            if self.__withIP:
                Preferences.setMicroPython("WifiApAddress", self.addressEdit.text())
                Preferences.setMicroPython("WifiApNetmask", self.netmaskEdit.text())
                Preferences.setMicroPython("WifiApGateway", self.gatewayEdit.text())
                Preferences.setMicroPython("WifiApDNS", self.dnsEdit.text())

            Preferences.syncPreferences()

        super().accept()

    def getApConfig(self):
        """
        Public method to get the entered access point configuration data.

        @return tuple containing the SSID, the password, the selected security mode
            and a tuple with the IPv4 address, the netmask, the gateway address and
            the resolver address
        @rtype tuple of (str, str, int, (str, str, str, str))
        """
        ifconfig = (
            (
                self.addressEdit.text(),
                self.netmaskEdit.text(),
                self.gatewayEdit.text(),
                self.dnsEdit.text(),
            )
            if self.__withIP
            else ("", "", "", "")
        )

        return (
            self.apSsidEdit.text(),
            self.apPasswordEdit.text(),
            self.apSecurityComboBox.currentData(),
            self.hostnameEdit.text(),
            ifconfig,
        )
