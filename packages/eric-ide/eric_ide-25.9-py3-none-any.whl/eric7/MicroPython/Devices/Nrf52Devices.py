# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the device interface class for NRF52 boards with UF2 support.
"""

import ast
import json

from PyQt6.QtCore import QUrl, pyqtSlot
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QMenu

from eric7 import EricUtilities, Preferences
from eric7.EricWidgets import EricMessageBox
from eric7.EricWidgets.EricApplication import ericApp

from ..MicroPythonWidget import HasQtChartsOrGraphs
from . import FirmwareGithubUrls
from .DeviceBase import BaseDevice


class Nrf52Device(BaseDevice):
    """
    Class implementing the device for NRF52 boards with UF2 support.
    """

    def __init__(self, microPythonWidget, deviceType, parent=None):
        """
        Constructor

        @param microPythonWidget reference to the main MicroPython widget
        @type MicroPythonWidget
        @param deviceType device type assigned to this device interface
        @type str
        @param parent reference to the parent object
        @type QObject
        """
        super().__init__(microPythonWidget, deviceType, parent)

        self.__createNrfMenu()

    def setButtons(self):
        """
        Public method to enable the supported action buttons.
        """
        super().setButtons()

        self.microPython.setActionButtons(
            run=True, repl=True, files=True, chart=HasQtChartsOrGraphs
        )

    def forceInterrupt(self):
        """
        Public method to determine the need for an interrupt when opening the
        serial connection.

        @return flag indicating an interrupt is needed
        @rtype bool
        """
        return False

    def deviceName(self):
        """
        Public method to get the name of the device.

        @return name of the device
        @rtype str
        """
        return self.tr("NRF52 with UF2")

    def canStartRepl(self):
        """
        Public method to determine, if a REPL can be started.

        @return tuple containing a flag indicating it is safe to start a REPL
            and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""

    def canStartPlotter(self):
        """
        Public method to determine, if a Plotter can be started.

        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""

    def canRunScript(self):
        """
        Public method to determine, if a script can be executed.

        @return tuple containing a flag indicating it is safe to start a
            Plotter and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""

    def runScript(self, script):
        """
        Public method to run the given Python script.

        @param script script to be executed
        @type str
        """
        pythonScript = script.split("\n")
        self.sendCommands(pythonScript)

    def canStartFileManager(self):
        """
        Public method to determine, if a File Manager can be started.

        @return tuple containing a flag indicating it is safe to start a
            File Manager and a reason why it cannot.
        @rtype tuple of (bool, str)
        """
        return True, ""

    def __createNrfMenu(self):
        """
        Private method to create the NRF52 submenu.
        """
        self.__nrfMenu = QMenu(self.tr("NRF52 Functions"))

        self.__showMpyAct = self.__nrfMenu.addAction(
            self.tr("Show MicroPython Versions"), self.__showFirmwareVersions
        )
        self.__nrfMenu.addSeparator()
        self.__bootloaderAct = self.__nrfMenu.addAction(
            self.tr("Activate Bootloader"), self.__activateBootloader
        )
        self.__flashMpyAct = self.__nrfMenu.addAction(
            self.tr("Flash MicroPython Firmware"), self.__flashPython
        )
        self.__nrfMenu.addSeparator()
        self.__resetAct = self.__nrfMenu.addAction(
            self.tr("Reset Device"), self.__resetDevice
        )

    def addDeviceMenuEntries(self, menu):
        """
        Public method to add device specific entries to the given menu.

        @param menu reference to the context menu
        @type QMenu
        """
        connected = self.microPython.isConnected()
        linkConnected = self.microPython.isLinkConnected()

        self.__showMpyAct.setEnabled(connected)
        self.__bootloaderAct.setEnabled(connected)
        self.__flashMpyAct.setEnabled(not linkConnected)
        self.__resetAct.setEnabled(connected)

        menu.addMenu(self.__nrfMenu)

    def hasFlashMenuEntry(self):
        """
        Public method to check, if the device has its own flash menu entry.

        @return flag indicating a specific flash menu entry
        @rtype bool
        """
        return True

    @pyqtSlot()
    def __flashPython(self):
        """
        Private slot to flash a MicroPython firmware to the device.
        """
        from ..UF2FlashDialog import UF2FlashDialog

        dlg = UF2FlashDialog(boardType="UF2 Board", parent=self.microPython)
        dlg.exec()

    @pyqtSlot()
    def __activateBootloader(self):
        """
        Private slot to switch the board into 'bootloader' mode.
        """
        if self.microPython.isConnected():
            self.executeCommands(
                [
                    "import machine",
                    "machine.bootloader()",
                ],
                mode=self._submitMode,
            )
            # simulate pressing the disconnect button
            self.microPython.on_connectButton_clicked()

    @pyqtSlot()
    def __showFirmwareVersions(self):
        """
        Private slot to show the firmware version of the connected device and the
        available firmware version.
        """
        if self.microPython.isConnected():
            if self._deviceData["mpy_name"] != "micropython":
                EricMessageBox.critical(
                    self.microPython,
                    self.tr("Show MicroPython Versions"),
                    self.tr(
                        """The firmware of the connected device cannot be"""
                        """ determined or the board does not run MicroPython."""
                        """ Aborting..."""
                    ),
                )
            else:
                url = QUrl(FirmwareGithubUrls["micropython"])
                ui = ericApp().getObject("UserInterface")
                request = QNetworkRequest(url)
                reply = ui.networkAccessManager().head(request)
                reply.finished.connect(lambda: self.__firmwareVersionResponse(reply))

    @pyqtSlot(QNetworkReply)
    def __firmwareVersionResponse(self, reply):
        """
        Private slot handling the response of the latest version request.

        @param reply reference to the reply object
        @type QNetworkReply
        """
        latestUrl = reply.url().toString()
        tag = latestUrl.rsplit("/", 1)[-1]
        while tag and not tag[0].isdecimal():
            # get rid of leading non-decimal characters
            tag = tag[1:]
        latestVersion = EricUtilities.versionToTuple(tag)

        if self._deviceData["mpy_version"] == "unknown":
            currentVersionStr = self.tr("unknown")
            currentVersion = (0, 0, 0)
        else:
            currentVersionStr = self._deviceData["mpy_version"]
            currentVersion = EricUtilities.versionToTuple(currentVersionStr)

        msg = self.tr(
            "<h4>MicroPython Version Information</h4>"
            "<table>"
            "<tr><td>Installed:</td><td>{0}</td></tr>"
            "<tr><td>Available:</td><td>{1}</td></tr>"
            "{2}"
            "</table>"
        ).format(
            currentVersionStr,
            tag,
            "",
        )
        if currentVersion < latestVersion:
            msg += self.tr("<p><b>Update available!</b></p>")

        EricMessageBox.information(
            self.microPython,
            self.tr("MicroPython Version"),
            msg,
        )

    @pyqtSlot()
    def __resetDevice(self):
        """
        Private slot to reset the connected device.
        """
        if self.microPython.isConnected():
            self.executeCommands(
                "import machine\nmachine.reset()\n", mode=self._submitMode
            )

    def getDocumentationUrl(self):
        """
        Public method to get the device documentation URL.

        @return documentation URL of the device
        @rtype str
        """
        return Preferences.getMicroPython("MicroPythonDocuUrl")

    def getDownloadMenuEntries(self):
        """
        Public method to retrieve the entries for the downloads menu.

        @return list of tuples with menu text and URL to be opened for each
            entry
        @rtype list of tuple of (str, str)
        """
        return [
            (
                self.tr("MicroPython Firmware"),
                Preferences.getMicroPython("MicroPythonFirmwareUrl"),
            ),
            ("<separator>", ""),
            (
                self.tr("CircuitPython Firmware"),
                Preferences.getMicroPython("CircuitPythonFirmwareUrl"),
            ),
            (
                self.tr("CircuitPython Libraries"),
                Preferences.getMicroPython("CircuitPythonLibrariesUrl"),
            ),
        ]

    ##################################################################
    ## Methods below implement Bluetooth related methods
    ##################################################################

    def hasBluetooth(self):
        """
        Public method to check the availability of Bluetooth.

        @return flag indicating the availability of Bluetooth
        @rtype bool
        @exception OSError raised to indicate an issue with the device
        """
        command = """
def has_bt():
    try:
        import ble
        if ble.address():
            return True
    except (ImportError, OSError):
        pass

    return False

print(has_bt())
del has_bt
"""
        out, err = self.executeCommands(command, mode=self._submitMode, timeout=10000)
        if err:
            raise OSError(self._shortError(err))
        return out.strip() == b"True"

    def getBluetoothStatus(self):
        """
        Public method to get Bluetooth status data of the connected board.

        @return list of tuples containing the translated status data label and
            the associated value
        @rtype list of tuples of (str, str)
        @exception OSError raised to indicate an issue with the device
        """
        command = """
def ble_status():
    import ble
    import json

    res = {
        'active': bool(ble.enabled()),
        'mac': ble.address(),
    }

    print(json.dumps(res))

ble_status()
del ble_status
"""
        out, err = self.executeCommands(command, mode=self._submitMode)
        if err:
            raise OSError(self._shortError(err))

        bleStatus = json.loads(out.decode("utf-8"))
        status = [
            (self.tr("Active"), self.bool2str(bleStatus["active"])),
            (self.tr("MAC-Address"), bleStatus["mac"]),
        ]

        return status

    def activateBluetoothInterface(self):
        """
        Public method to activate the Bluetooth interface.

        @return flag indicating the new state of the Bluetooth interface
        @rtype bool
        @exception OSError raised to indicate an issue with the device
        """
        command = """
def activate_ble():
    import ble

    if not ble.enabled():
        ble.enable()
    print(bool(ble.enabled()))

activate_ble()
del activate_ble
"""
        out, err = self.executeCommands(command, mode=self._submitMode)
        if err:
            raise OSError(self._shortError(err))

        return out.strip() == b"True"

    def deactivateBluetoothInterface(self):
        """
        Public method to deactivate the Bluetooth interface.

        @return flag indicating the new state of the Bluetooth interface
        @rtype bool
        @exception OSError raised to indicate an issue with the device
        """
        command = """
def deactivate_ble():
    import ble

    if ble.enabled():
        ble.disable()
    print(bool(ble.enabled()))

deactivate_ble()
del deactivate_ble
"""
        out, err = self.executeCommands(command, mode=self._submitMode)
        if err:
            raise OSError(self._shortError(err))

        return out.strip() == b"True"

    def getDeviceScan(self, timeout=10):
        """
        Public method to perform a Bluetooth device scan.

        @param timeout duration of the device scan in seconds (defaults
            to 10)
        @type int (optional)
        @return tuple containing a dictionary with the scan results and
            an error string
        @rtype tuple of (dict, str)
        """
        from ..BluetoothDialogs.BluetoothAdvertisement import (
            SCAN_RSP,
            BluetoothAdvertisement,
        )

        command = """
def ble_scan():
    import ble
    import ubluepy as ub

    ble_active = ble.enabled()
    if not ble_active:
        ble.enable()

    sc = ub.Scanner()
    scanResults = sc.scan({0} * 1000)
    for res in scanResults:
        try:
            scanData = res.getScanData()
            if res.addr():
                for data in scanData:
                    print({{
                        'address': res.addr(),
                        'rssi': res.rssi(),
                        'adv_type': data[0],
                        'advertisement': bytes(data[2]),
                    }})
        except MemoryError:
            pass

    if not ble_active:
        ble.disable()

ble_scan()
del ble_scan
""".format(
            timeout
        )
        out, err = self.executeCommands(
            command, mode=self._submitMode, timeout=(timeout + 5) * 1000
        )
        if err:
            return {}, err

        scanResults = {}
        tempResults = {}

        for line in out.decode("utf-8").splitlines():
            res = ast.literal_eval(line)
            address = res["address"]
            if address not in tempResults:
                tempResults[address] = {
                    "advertisements": {},
                }
            tempResults[address]["rssi"] = res["rssi"]
            tempResults[address]["advertisements"][res["adv_type"]] = res[
                "advertisement"
            ]

        for address in tempResults:
            advertisements = bytearray()
            for advType, advertisement in tempResults[address][
                "advertisements"
            ].items():
                advertisements += (
                    (len(advertisement) + 1).to_bytes()
                    + advType.to_bytes()
                    + advertisement
                )
            scanResults[address] = BluetoothAdvertisement(address)
            scanResults[address].update(
                SCAN_RSP, tempResults[address]["rssi"], advertisements
            )

        return scanResults, ""

    def supportsDeviceScan(self):
        """
        Public method to indicate, that the Bluetooth implementation supports
        scanning for devices.

        @return flag indicating that the scanning function is supported
        @rtype bool
        """
        return True


def createDevice(microPythonWidget, deviceType, _vid, _pid, _boardName, _serialNumber):
    """
    Function to instantiate a MicroPython device object.

    @param microPythonWidget reference to the main MicroPython widget
    @type MicroPythonWidget
    @param deviceType device type assigned to this device interface
    @type str
    @param _vid vendor ID (unused)
    @type int
    @param _pid product ID (unused)
    @type int
    @param _boardName name of the board (unused)
    @type str
    @param _serialNumber serial number of the board (unused)
    @type str
    @return reference to the instantiated device object
    @rtype RP2Device
    """
    return Nrf52Device(microPythonWidget, deviceType)
