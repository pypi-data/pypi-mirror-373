# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing a dialog to enter a file to be processed.
"""

import os

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from eric7.EricWidgets.EricPathPicker import EricPathPickerModes

from .Ui_PipFileSelectionDialog import Ui_PipFileSelectionDialog


class PipFileSelectionDialog(QDialog, Ui_PipFileSelectionDialog):
    """
    Class implementing a dialog to enter a file to be processed.
    """

    def __init__(self, mode, install=True, parent=None):
        """
        Constructor

        @param mode mode of the dialog
        @type str
        @param install flag indicating an install action
        @type bool
        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)

        self.__mode = mode

        if mode == "requirements":
            self.fileLabel.setText(self.tr("Enter requirements file:"))
            self.filePicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
            self.filePicker.setToolTip(
                self.tr(
                    "Press to select the requirements file through a file"
                    " selection dialog."
                )
            )
            self.filePicker.setFilters(self.tr("Text Files (*.txt);;All Files (*)"))
        elif mode == "pyproject":
            self.fileLabel.setText(self.tr("Enter 'pyproject.toml' file:"))
            self.filePicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
            self.filePicker.setToolTip(
                self.tr(
                    "Press to select the 'pyproject.toml' file through a file"
                    " selection dialog."
                )
            )
            self.filePicker.setFilters(self.tr("TOML Files (*.toml);;All Files (*)"))
        elif mode == "package":
            self.fileLabel.setText(self.tr("Enter package file:"))
            self.filePicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
            self.filePicker.setToolTip(
                self.tr(
                    "Press to select the package file through a file"
                    " selection dialog."
                )
            )
            self.filePicker.setFilters(
                self.tr(
                    "Python Wheel (*.whl);;"
                    "Archive Files (*.tar.gz *.zip);;"
                    "All Files (*)"
                )
            )
        else:
            self.fileLabel.setText(self.tr("Enter file name:"))
            self.filePicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
            self.filePicker.setToolTip(
                self.tr("Press to select a file through a file selection dialog.")
            )
            self.filePicker.setFilters(self.tr("All Files (*)"))
        self.filePicker.setDefaultDirectory(os.path.expanduser("~"))

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        self.filePicker.textChanged.connect(self.__updateOk)
        self.specificDepsButton.toggled.connect(self.__updateOk)
        self.specificDepsEdit.textChanged.connect(self.__updateOk)

        if mode != "pyproject" or not install:
            self.dependenciesGroupBox.hide()
        self.userCheckBox.setVisible(install)

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    @pyqtSlot()
    def __updateOk(self):
        """
        Private slot to set the state of the OK button.
        """
        filePath = self.filePicker.text()
        enable = bool(filePath) and os.path.exists(filePath)
        if self.__mode == "pyproject" and self.specificDepsButton.isChecked():
            enable &= bool(self.specificDepsEdit.text())

        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enable)

    def getData(self):
        """
        Public method to retrieve the entered data.

        @return tuple containing the path of the selected file, a flag indicating to
            install all optional dependencies a list of specific dependencies to
            be installed and a flag indicating to install to the user install directory
        @rtype tuple of (str, bool, list of str, bool)
        """
        return (
            self.filePicker.text(),
            self.allDepsButton.isChecked(),
            (
                [e.strip() for e in self.specificDepsEdit.text().split()]
                if self.specificDepsButton.isChecked()
                else []
            ),
            self.userCheckBox.isChecked(),
        )
