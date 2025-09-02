# -*- coding: utf-8 -*-

# Copyright (c) 2018 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the data of a virtual environment.
"""

import os

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7.EricWidgets.EricApplication import ericApp
from eric7.EricWidgets.EricPathPicker import EricPathPickerModes
from eric7.SystemUtilities import FileSystemUtilities, OSUtilities, PythonUtilities

from .Ui_VirtualenvAddEditDialog import Ui_VirtualenvAddEditDialog
from .VirtualenvMeta import VirtualenvMetaData


class VirtualenvAddEditDialog(QDialog, Ui_VirtualenvAddEditDialog):
    """
    Class implementing a dialog to enter the data of a virtual environment.
    """

    def __init__(
        self,
        manager,
        metadata=None,
        baseDir="",
        parent=None,
    ):
        """
        Constructor

        @param manager reference to the virtual environment manager
        @type VirtualenvManager
        @param metadata object containing the metadata of the virtual environment
            (defaults to None)
        @type VirtualenvMetaData (optional)
        @param baseDir base directory for the virtual environments (defaults to "")
        @type str (optional)
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        self.__venvName = "" if metadata is None else metadata.name
        self.__manager = manager
        self.__editMode = bool(self.__venvName)
        try:
            self.__serverInterface = ericApp().getObject("EricServer")
            self.__fsInterface = self.__serverInterface.getServiceInterface(
                "FileSystem"
            )
        except KeyError:
            self.__serverInterface = None
            self.__fsInterface = None

        if self.__editMode:
            self.setWindowTitle(self.tr("Edit Virtual Environment"))
        else:
            self.setWindowTitle(self.tr("Add Virtual Environment"))

        for name, visualName in self.__manager.getEnvironmentTypeNames():
            self.environmentTypeComboBox.addItem(visualName, name)

        self.__envBaseDir = baseDir
        if not self.__envBaseDir:
            self.__envBaseDir = OSUtilities.getHomeDir()

        self.targetDirectoryPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.targetDirectoryPicker.setWindowTitle(
            self.tr("Virtualenv Target Directory")
        )
        if (
            self.__serverInterface is not None
            and self.__serverInterface.isServerConnected()
        ):
            self.targetDirectoryPicker.setRemote(
                metadata.environment_type == "eric_server" if metadata else False
            )
        if metadata is None or metadata.environment_type not in (
            "eric_server",
            "remote",
        ):
            self.targetDirectoryPicker.setDefaultDirectory(self.__envBaseDir)

        self.pythonExecPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.pythonExecPicker.setWindowTitle(self.tr("Python Interpreter"))
        if (
            self.__serverInterface is not None
            and self.__serverInterface.isServerConnected()
        ):
            self.pythonExecPicker.setRemote(
                metadata.environment_type == "eric_server" if metadata else False
            )
        if metadata is None or metadata.environment_type not in (
            "eric_server",
            "remote",
        ):
            self.pythonExecPicker.setDefaultDirectory(
                PythonUtilities.getPythonExecutable()
            )

        self.execPathEdit.setToolTip(
            self.tr(
                "Enter the executable search path to be prepended to the PATH"
                " environment variable. Use '{0}' as the separator."
            ).format(os.pathsep)
        )

        self.nameEdit.setText(self.__venvName)
        if metadata:
            if metadata.path:
                self.targetDirectoryPicker.setText(
                    metadata.path,
                    toNative=metadata.environment_type not in ("eric_server", "remote"),
                )
            else:
                self.targetDirectoryPicker.setText(
                    self.__envBaseDir,
                    toNative=metadata.environment_type not in ("eric_server", "remote"),
                )
            if (
                not metadata.interpreter
                and metadata.path
                and metadata.environment_type not in ("eric_server", "remote")
            ):
                py = self.__detectPythonInterpreter(metadata.path)
                self.pythonExecPicker.setText(py)
            else:
                self.pythonExecPicker.setText(
                    metadata.interpreter,
                    toNative=metadata.environment_type not in ("eric_server", "remote"),
                )
        else:
            self.targetDirectoryPicker.setText(self.__envBaseDir, toNative=True)

        self.globalCheckBox.setChecked(metadata.is_global if metadata else False)
        self.availableCheckBox.setChecked(metadata.available if metadata else True)
        itemIndex = self.environmentTypeComboBox.findData(
            metadata.environment_type if metadata else "standard"
        )
        self.environmentTypeComboBox.setCurrentIndex(itemIndex)
        self.execPathEdit.setText(metadata.exec_path if metadata else "")
        self.descriptionEdit.setPlainText(metadata.description if metadata else "")
        self.serverLineEdit.setText(metadata.eric_server if metadata else "")

        self.__updateOk()

        self.nameEdit.setFocus(Qt.FocusReason.OtherFocusReason)

    def __updateOk(self):
        """
        Private slot to update the state of the OK button.
        """
        enable = (
            (
                bool(self.nameEdit.text())
                and (
                    self.nameEdit.text() == self.__venvName
                    or self.__manager.isUnique(self.nameEdit.text())
                )
            )
            if self.__editMode
            else (
                bool(self.nameEdit.text())
                and self.__manager.isUnique(self.nameEdit.text())
            )
        )

        selectedVenvType = self.environmentTypeComboBox.currentData()
        if not self.globalCheckBox.isChecked():
            enable &= selectedVenvType == "remote" or (
                bool(self.targetDirectoryPicker.text())
                and self.targetDirectoryPicker.text() != self.__envBaseDir
                and (
                    (
                        selectedVenvType == "eric_server"
                        and self.__fsInterface is not None
                        and self.__fsInterface.exists(self.targetDirectoryPicker.text())
                    )
                    or (
                        selectedVenvType != "eric_server"
                        and os.path.exists(self.targetDirectoryPicker.text())
                    )
                )
            )

        enable &= selectedVenvType == "remote" or (
            bool(self.pythonExecPicker.text())
            and (
                (
                    selectedVenvType == "eric_server"
                    and self.__fsInterface is not None
                    and self.__fsInterface.access(
                        self.pythonExecPicker.text(), "execute"
                    )
                )
                or (
                    selectedVenvType != "eric_server"
                    and os.access(self.pythonExecPicker.text(), os.X_OK)
                )
            )
        )

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    def __detectPythonInterpreter(self, venvDirectory):
        """
        Private method to search for a suitable Python interpreter inside an
        environment.

        @param venvDirectory directory for the virtual environment
        @type str
        @return detected Python interpreter or empty string
        @rtype str
        """
        if venvDirectory:
            # try to determine a Python interpreter name
            if OSUtilities.isWindowsPlatform():
                candidates = (
                    os.path.join(venvDirectory, "Scripts", "python.exe"),
                    os.path.join(venvDirectory, "python.exe"),
                )
            else:
                candidates = (os.path.join(venvDirectory, "bin", "python3"),)
            for py in candidates:
                if os.path.exists(py):
                    return py

        return ""

    @pyqtSlot(str)
    def on_nameEdit_textChanged(self, txt):
        """
        Private slot to handle changes of the logical name.

        @param txt current logical name
        @type str
        """
        self.__updateOk()

    @pyqtSlot(str)
    def on_targetDirectoryPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment directory.

        @param txt virtual environment directory
        @type str
        """
        self.__updateOk()

        if txt:
            self.pythonExecPicker.setDefaultDirectory(txt)
        else:
            self.pythonExecPicker.setDefaultDirectory(
                PythonUtilities.getPythonExecutable()
            )
        py = self.__detectPythonInterpreter(txt)
        if py:
            self.pythonExecPicker.setText(py)

    @pyqtSlot(str)
    def on_pythonExecPicker_textChanged(self, txt):
        """
        Private slot to handle changes of the virtual environment interpreter.

        @param txt virtual environment interpreter
        @type str
        """
        self.__updateOk()

    @pyqtSlot(bool)
    def on_globalCheckBox_toggled(self, checked):
        """
        Private slot handling a change of the global check box state.

        @param checked state of the check box
        @type bool
        """
        self.__updateOk()

    @pyqtSlot(int)
    def on_environmentTypeComboBox_currentIndexChanged(self, index):
        """
        Private slot handling the selection of a virtual environment type.

        @param index index of the selected virtual environment type
        @type int
        """
        # step 1: reset some configurations
        self.pythonExecPicker.setRemote(False)
        self.targetDirectoryPicker.setRemote(False)
        self.serverLineEdit.clear()
        self.ericServerInfoLabel.clear()

        # step 2: configure and set value iaw. selected environment type
        selectedVenvType = self.environmentTypeComboBox.itemData(index)
        if selectedVenvType == "eric_server":
            serverAvailable = (
                self.__serverInterface is not None
                and self.__serverInterface.isServerConnected()
            )
            self.ericServerInfoLabel.setText(
                "" if serverAvailable else self.tr("eric-ide Server is not available")
            )
            self.pythonExecPicker.setRemote(serverAvailable)
            self.targetDirectoryPicker.setRemote(serverAvailable)
            if serverAvailable:
                self.targetDirectoryPicker.setText(self.__fsInterface.getcwd())
                self.serverLineEdit.setText(self.__serverInterface.getHost())

        venvTypeData = self.__manager.getEnvironmentTypesRegistry().getEnvironmentType(
            selectedVenvType
        )
        if venvTypeData.defaultExecPathFunc is not None and not bool(
            self.execPathEdit.text()
        ):
            self.execPathEdit.setText(
                venvTypeData.defaultExecPathFunc(self.targetDirectoryPicker.text())
            )

        self.__updateOk()

    def getMetaData(self):
        """
        Public method to retrieve the entered metadata.

        @return metadata for the virtual environment
        @rtype VirtualenvMetaData
        """
        selectedEnvironmentType = self.environmentTypeComboBox.currentData()
        nativePaths = selectedEnvironmentType not in ("remote", "eric_server")
        isEricServer = selectedEnvironmentType == "eric_server"
        envPath = (
            FileSystemUtilities.remoteFileName(self.targetDirectoryPicker.text())
            if isEricServer
            else FileSystemUtilities.plainFileName(
                self.targetDirectoryPicker.text(toNative=nativePaths)
            )
        )
        interpreter = (
            FileSystemUtilities.remoteFileName(self.pythonExecPicker.text())
            if isEricServer
            else FileSystemUtilities.plainFileName(
                self.pythonExecPicker.text(toNative=nativePaths)
            )
        )

        return VirtualenvMetaData(
            name=self.nameEdit.text(),
            path=envPath,
            interpreter=interpreter,
            is_global=self.globalCheckBox.isChecked(),
            environment_type=selectedEnvironmentType,
            exec_path=self.execPathEdit.text(),
            description=self.descriptionEdit.toPlainText(),
            eric_server=self.serverLineEdit.text(),
            available=self.availableCheckBox.isChecked(),
        )
