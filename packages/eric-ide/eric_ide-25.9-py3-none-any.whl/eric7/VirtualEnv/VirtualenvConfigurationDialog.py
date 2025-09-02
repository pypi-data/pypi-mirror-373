# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to enter the parameters for the
virtual environment.
"""

import os
import re

from PyQt6.QtCore import QProcess, QTimer, pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7 import Preferences
from eric7.EricWidgets.EricApplication import ericApp
from eric7.EricWidgets.EricPathPicker import EricPathPickerModes
from eric7.SystemUtilities import PythonUtilities

from .Ui_VirtualenvConfigurationDialog import Ui_VirtualenvConfigurationDialog


class VirtualenvConfigurationDialog(QDialog, Ui_VirtualenvConfigurationDialog):
    """
    Class implementing a dialog to enter the parameters for the virtual environment.
    """

    def __init__(self, baseDir="", parent=None):
        """
        Constructor

        @param baseDir base directory for the virtual environments
        @type str
        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)

        if not baseDir:
            baseDir = os.path.expanduser("~")
        self.__envBaseDir = baseDir

        self.targetDirectoryPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.targetDirectoryPicker.setWindowTitle(
            self.tr("Virtualenv Target Directory")
        )
        self.targetDirectoryPicker.setText(baseDir)
        self.targetDirectoryPicker.setDefaultDirectory(baseDir)

        self.extraSearchPathPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.extraSearchPathPicker.setWindowTitle(
            self.tr("Extra Search Path for setuptools/pip")
        )
        self.extraSearchPathPicker.setDefaultDirectory(os.path.expanduser("~"))

        self.pythonExecPicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.pythonExecPicker.setWindowTitle(self.tr("Python Interpreter"))
        self.pythonExecPicker.setDefaultDirectory(PythonUtilities.getPythonExecutable())

        self.versionComboBox.addItems(["", "3.13", "3.12", "3.11", "3.10", "3.9"])

        self.__versionRe = re.compile(r""".*?(\d+\.\d+\.\d+).*""")

        self.__virtualenvFound = False
        self.__pyvenvFound = False
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        self.__mandatoryStyleSheet = (
            "QLineEdit {border: 2px solid; border-color: #dd8888}"
            if ericApp().usesDarkPalette()
            else "QLineEdit {border: 2px solid; border-color: #800000}"
        )
        self.targetDirectoryPicker.setStyleSheet(self.__mandatoryStyleSheet)
        self.nameEdit.setStyleSheet(self.__mandatoryStyleSheet)

        self.__setVirtualenvVersion()
        self.__setPyvenvVersion()
        if self.__pyvenvFound:
            self.pyvenvButton.setChecked(True)
        elif self.__virtualenvFound:
            self.virtualenvButton.setChecked(True)

        self.nameEdit.textChanged.connect(self.__updateOK)
        self.targetDirectoryPicker.textChanged.connect(self.__updateOK)
        self.virtualenvButton.toggled.connect(self.__updateUi)
        self.pyvenvButton.toggled.connect(self.__updateUi)

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    @pyqtSlot()
    def __updateOK(self):
        """
        Private slot to update the enabled status of the OK button.
        """
        if self.virtualenvButton.isChecked() or self.pyvenvButton.isChecked():
            enable = (
                (self.__virtualenvFound or self.__pyvenvFound)
                and bool(self.targetDirectoryPicker.text())
                and bool(self.nameEdit.text())
            )
            enable &= self.targetDirectoryPicker.text() != self.__envBaseDir
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    @pyqtSlot()
    def __updateUi(self):
        """
        Private slot to update the UI depending on the selected
        virtual environment creator (virtualenv or pyvenv).
        """
        enable = self.virtualenvButton.isChecked()
        self.extraSearchPathLabel.setEnabled(enable)
        self.extraSearchPathPicker.setEnabled(enable)
        self.promptPrefixLabel.setEnabled(enable)
        self.promptPrefixEdit.setEnabled(enable)
        self.verbosityLabel.setEnabled(enable)
        self.verbositySpinBox.setEnabled(enable)
        self.versionLabel.setEnabled(enable)
        self.versionComboBox.setEnabled(enable)
        self.noWheelCheckBox.setEnabled(enable)
        self.noSetuptoolsCheckBox.setEnabled(enable)
        self.symlinkCheckBox.setEnabled(not enable)
        self.upgradeCheckBox.setEnabled(not enable)

    @pyqtSlot(str)
    def on_pythonExecPicker_textChanged(self, _txt):
        """
        Private slot to react to a change of the Python executable.

        @param _txt contents of the picker's line edit (unused)
        @type str
        """
        self.__setVirtualenvVersion()
        self.__setPyvenvVersion()
        self.__updateOK()

    def __setVirtualenvVersion(self):
        """
        Private method to determine the virtualenv version and set the
        respective label.
        """
        calls = []
        if self.pythonExecPicker.text():
            calls.append(
                (self.pythonExecPicker.text(), ["-m", "virtualenv", "--version"])
            )
        calls.extend(
            [
                (
                    PythonUtilities.getPythonExecutable(),
                    ["-m", "virtualenv", "--version"],
                ),
                ("virtualenv", ["--version"]),
            ]
        )

        proc = QProcess()
        for prog, args in calls:
            proc.start(prog, args)

            if not proc.waitForStarted(5000):
                # try next entry
                continue

            if not proc.waitForFinished(5000):
                # process hangs, kill it
                QTimer.singleShot(2000, proc.kill)
                proc.waitForFinished(3000)
                version = self.tr("<virtualenv did not finish within 5s.>")
                self.__virtualenvFound = False
                break

            if proc.exitCode() != 0:
                # returned with error code, try next
                continue

            output = str(
                proc.readAllStandardOutput(),
                Preferences.getSystem("IOEncoding"),
                "replace",
            ).strip()
            match = re.match(self.__versionRe, output)
            if match:
                self.__virtualenvFound = True
                version = match.group(1)
                break
        else:
            self.__virtualenvFound = False
            version = self.tr("<No suitable virtualenv found.>")

        self.virtualenvButton.setText(
            self.tr("virtualenv Version: {0}".format(version))
        )
        self.virtualenvButton.setEnabled(self.__virtualenvFound)
        if not self.__virtualenvFound:
            self.virtualenvButton.setChecked(False)

    def __setPyvenvVersion(self):
        """
        Private method to determine the pyvenv version and set the respective
        label.
        """
        calls = []
        if self.pythonExecPicker.text():
            calls.append((self.pythonExecPicker.text(), ["-m", "venv"]))
        calls.extend(
            [
                (PythonUtilities.getPythonExecutable(), ["-m", "venv"]),
                ("python3", ["-m", "venv"]),
                ("python", ["-m", "venv"]),
            ]
        )

        proc = QProcess()
        for prog, args in calls:
            proc.start(prog, args)

            if not proc.waitForStarted(5000):
                # try next entry
                continue

            if not proc.waitForFinished(5000):
                # process hangs, kill it
                QTimer.singleShot(2000, proc.kill)
                proc.waitForFinished(3000)
                version = self.tr("<pyvenv did not finish within 5s.>")
                self.__pyvenvFound = False
                break

            if proc.exitCode() not in [0, 2]:
                # returned with error code, try next
                continue

            proc.start(prog, ["--version"])
            proc.waitForFinished(5000)
            output = str(
                proc.readAllStandardOutput(),
                Preferences.getSystem("IOEncoding"),
                "replace",
            ).strip()
            match = re.match(self.__versionRe, output)
            if match:
                self.__pyvenvFound = True
                version = match.group(1)
                break
        else:
            self.__pyvenvFound = False
            version = self.tr("<No suitable pyvenv found.>")

        self.pyvenvButton.setText(self.tr("pyvenv Version: {0}".format(version)))
        self.pyvenvButton.setEnabled(self.__pyvenvFound)
        if not self.__pyvenvFound:
            self.pyvenvButton.setChecked(False)

    def __generateTargetDir(self):
        """
        Private method to generate a valid target directory path.

        @return target directory path
        @rtype str
        """
        targetDirectory = self.targetDirectoryPicker.text()
        if not os.path.isabs(targetDirectory):
            targetDirectory = os.path.join(os.path.expanduser("~"), targetDirectory)
        return targetDirectory

    def __generateArguments(self):
        """
        Private method to generate the process arguments.

        @return process arguments
        @rtype list of str
        """
        args = []
        if self.virtualenvButton.isChecked():
            if self.extraSearchPathPicker.text():
                args.append(
                    "--extra-search-dir={0}".format(self.extraSearchPathPicker.text())
                )
            if self.promptPrefixEdit.text():
                args.append(
                    "--prompt={0}".format(
                        self.promptPrefixEdit.text().replace(" ", "_")
                    )
                )
            if self.pythonExecPicker.text():
                args.append("--python={0}".format(self.pythonExecPicker.text()))
            elif self.versionComboBox.currentText():
                args.append(
                    "--python=python{0}".format(self.versionComboBox.currentText())
                )
            if self.verbositySpinBox.value() == 1:
                args.append("--verbose")
            elif self.verbositySpinBox.value() == -1:
                args.append("--quiet")
            if self.clearCheckBox.isChecked():
                args.append("--clear")
            if self.systemCheckBox.isChecked():
                args.append("--system-site-packages")
            if self.noWheelCheckBox.isChecked():
                args.append("--no-wheel")
            if self.noSetuptoolsCheckBox.isChecked():
                args.append("--no-setuptools")
            if self.noPipCcheckBox.isChecked():
                args.append("--no-pip")
            if self.copyCheckBox.isChecked():
                args.append("--always-copy")
        elif self.pyvenvButton.isChecked():
            if self.clearCheckBox.isChecked():
                args.append("--clear")
            if self.systemCheckBox.isChecked():
                args.append("--system-site-packages")
            if self.noPipCcheckBox.isChecked():
                args.append("--without-pip")
            if self.copyCheckBox.isChecked():
                args.append("--copies")
            if self.symlinkCheckBox.isChecked():
                args.append("--symlinks")
            if self.upgradeCheckBox.isChecked():
                args.append("--upgrade")
        targetDirectory = self.__generateTargetDir()
        args.append(targetDirectory)

        return args

    def getData(self):
        """
        Public method to retrieve the dialog data.

        @return dictionary containing the data for the new environment. The keys
            are 'arguments' containing the command line arguments, 'logicalName'
            containing the environment name to be used with the virtual environment
            manager and 'envType' containing the environment type (virtualenv or
            pyvenv). Additional keys are 'openTarget' containg a flag to open the
            target directory after creation, 'createLog' containing a flag to write
            a log file, 'createScript' containing a flag to write a script,
            'targetDirectory' containing the target directory and 'pythonExe'
            containing the Python interpreter to be used.
        @rtype dict
        """
        return {
            "arguments": self.__generateArguments(),
            "logicalName": self.nameEdit.text(),
            "envType": "pyvenv" if self.pyvenvButton.isChecked() else "virtualenv",
            "openTarget": self.openCheckBox.isChecked(),
            "createLog": self.logCheckBox.isChecked(),
            "createScript": self.scriptCheckBox.isChecked(),
            "targetDirectory": self.__generateTargetDir(),
            "pythonExe": self.pythonExecPicker.text(),
        }
