# -*- coding: utf-8 -*-

# Copyright (c) 2022 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to configure the CycloneDX SBOM generation.
"""

import os

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog

from eric7.EricWidgets.EricApplication import ericApp
from eric7.EricWidgets.EricPathPicker import EricPathPickerModes

from .Ui_CycloneDXConfigDialog import Ui_CycloneDXConfigDialog


class CycloneDXConfigDialog(QDialog, Ui_CycloneDXConfigDialog):
    """
    Class implementing a dialog to configure the CycloneDX SBOM generation.
    """

    SupportedSpecs = {
        "JSON": [
            (1, 6),
            (1, 5),
            (1, 4),
            (1, 3),
            (1, 2),
        ],
        "XML": [
            (1, 6),
            (1, 5),
            (1, 4),
            (1, 3),
            (1, 2),
            (1, 1),
            (1, 0),
        ],
    }
    Sources = {
        "pipenv": "Pipfile.lock",
        "poetry": "poetry.lock",
        "requirements": "requirements.txt",
    }
    DefaultFileFormat = "JSON"
    DefaultFileNames = {
        "JSON": "cyclonedx.json",
        "XML": "cyclonedx.xml",
    }

    def __init__(self, environment, parent=None):
        """
        Constructor

        @param environment name of the virtual environment
        @type str
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        for componentTypeStr, componentType in [
            (self.tr("Application"), "application"),
            (self.tr("Firmware"), "firmware"),
            (self.tr("Library"), "library"),
        ]:
            self.mainComponentTypeComboBox.addItem(componentTypeStr, componentType)

        if environment == "<project>":
            self.__project = ericApp().getObject("Project")
            self.__defaultDirectory = self.__project.getProjectPath()
        else:
            self.__project = None
            venvManager = ericApp().getObject("VirtualEnvManager")
            self.__defaultDirectory = venvManager.getVirtualenvDirectory(environment)

        self.environmentLabel.setText(environment)

        self.pipenvButton.setEnabled(
            os.path.isfile(
                os.path.join(
                    self.__defaultDirectory, CycloneDXConfigDialog.Sources["pipenv"]
                )
            )
        )
        self.poetryButton.setEnabled(
            os.path.isfile(
                os.path.join(
                    self.__defaultDirectory, CycloneDXConfigDialog.Sources["poetry"]
                )
            )
        )
        self.requirementsButton.setEnabled(
            os.path.isfile(
                os.path.join(
                    self.__defaultDirectory,
                    CycloneDXConfigDialog.Sources["requirements"],
                )
            )
        )

        self.pyprojectFilePicker.setMode(EricPathPickerModes.OPEN_FILE_MODE)
        self.pyprojectFilePicker.setDefaultDirectory(self.__defaultDirectory)
        self.pyprojectFilePicker.setFilters(
            self.tr("TOML Files (*.toml);;All Files (*)")
        )

        self.outputFilePicker.setMode(
            EricPathPickerModes.SAVE_FILE_ENSURE_EXTENSION_MODE
        )
        self.outputFilePicker.setDefaultDirectory(self.__defaultDirectory)

        self.fileFormatComboBox.setCurrentText(CycloneDXConfigDialog.DefaultFileFormat)
        self.on_fileFormatComboBox_currentTextChanged(
            CycloneDXConfigDialog.DefaultFileFormat
        )

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    @pyqtSlot()
    def __repopulateSpecVersionComboBox(self):
        """
        Private slot to repopulate the spec version selector.
        """
        fileFormat = self.fileFormatComboBox.currentText()

        self.specVersionComboBox.clear()
        self.specVersionComboBox.addItems(
            "{0}.{1}".format(*f)
            for f in CycloneDXConfigDialog.SupportedSpecs[fileFormat]
        )

    @pyqtSlot(bool)
    def on_poetryButton_toggled(self, checked):
        """
        Private slot handling a change of the 'Poetry' button state.

        @param checked state of the button
        @type bool
        """
        self.pyprojectLabel.setEnabled(not checked)
        self.pyprojectFilePicker.setEnabled(not checked)
        if checked:
            self.pyprojectFilePicker.clear()

    @pyqtSlot(str)
    def on_fileFormatComboBox_currentTextChanged(self, fileFormat):
        """
        Private slot to handle the selection of a SBOM file format.

        @param fileFormat selected format
        @type str
        """
        # re-populate the file schema combo box
        self.__repopulateSpecVersionComboBox()

        # set the file filter
        if fileFormat == "JSON":
            self.outputFilePicker.setFilters(
                self.tr("JSON Files (*.json);;All Files (*)")
            )
            suffix = ".json"
        elif fileFormat == "XML":
            self.outputFilePicker.setFilters(
                self.tr("XML Files (*.xml);;All Files (*)")
            )
            suffix = ".xml"
        else:
            self.outputFilePicker.setFilters(self.tr("All Files (*)"))
            suffix = ""

        filePath = self.outputFilePicker.path()
        if bool(filePath.name):
            self.outputFilePicker.setPath(filePath.with_suffix(suffix))

    def getData(self):
        """
        Public method to get the SBOM configuration data.

        @return tuple containing the input source, the input path name, the
            file format, the schema version, the path of the SBOM file to be
            written, the path to the pyproject.toml file and the type of the
            main component.
        @rtype tuple of (str, str, str, str, str, str, str)
        """
        if self.environmentButton.isChecked():
            inputSource = "environment"
            if self.environmentLabel.text() == "<project>":
                inputPath = self.__project.getProjectInterpreter()
            else:
                inputPath = self.__defaultDirectory
        elif self.pipenvButton.isChecked():
            inputSource = "pipenv"
            inputPath = self.__defaultDirectory
        elif self.poetryButton.isChecked():
            inputSource = "poetry"
            inputPath = self.__defaultDirectory
        elif self.requirementsButton.isChecked():
            inputSource = "requirements"
            inputPath = os.path.join(
                self.__defaultDirectory, CycloneDXConfigDialog.Sources["requirements"]
            )
        else:
            # should not happen
            inputSource = None
            inputPath = None

        fileFormat = self.fileFormatComboBox.currentText()
        specVersion = self.specVersionComboBox.currentText()
        sbomFile = self.outputFilePicker.text()
        if not sbomFile:
            try:
                sbomFile = os.path.join(
                    self.__defaultDirectory,
                    CycloneDXConfigDialog.DefaultFileNames[fileFormat],
                )
            except KeyError:
                # should not happen
                sbomFile = None

        return (
            inputSource,
            inputPath,
            fileFormat,
            specVersion,
            sbomFile,
            self.pyprojectFilePicker.text(),
            self.mainComponentTypeComboBox.currentData(),
        )
