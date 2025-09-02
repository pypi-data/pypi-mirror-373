# -*- coding: utf-8 -*-

# Copyright (c) 2022 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the interface to CycloneDX.
"""

import os
import sys

from PyQt6.QtCore import QCoreApplication, QProcess
from PyQt6.QtWidgets import QDialog

from eric7 import Preferences
from eric7.EricWidgets import EricMessageBox


def createCycloneDXFile(venvName, parent=None):
    """
    Function to create a CyccloneDX SBOM file.

    @param venvName name of the virtual environment
    @type str
    @param parent referent to a parent widget (defaults to None)
    @type QWidget (optional)
    @exception RuntimeError raised to indicate illegal creation parameters
    """
    from .CycloneDXConfigDialog import CycloneDXConfigDialog

    dlg = CycloneDXConfigDialog(venvName, parent=parent)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        (
            inputSource,
            inputPath,
            fileFormat,
            specVersion,
            sbomFile,
            pyprojectFile,
            mainComponentType,
        ) = dlg.getData()

        # check error conditions first
        if inputSource not in ("environment", "pipenv", "poetry", "requirements"):
            raise RuntimeError("Unsupported input source given.")
        if fileFormat not in ("XML", "JSON"):
            raise RuntimeError("Unsupported SBOM file format given.")

        args = [
            inputSource,
            "--mc-type",
            mainComponentType,
            "--spec-version",
            specVersion,
            "--output-format",
            fileFormat,
            "--output-file",
            sbomFile,
        ]
        if pyprojectFile:
            args.extend(["--pyproject", pyprojectFile])

        args.append(inputPath)
        prog = os.path.join(os.path.dirname(sys.executable), "cyclonedx-py")
        process = QProcess()
        process.start(prog, args)
        if process.waitForStarted():
            if process.waitForFinished():
                if process.exitCode() == 0:
                    EricMessageBox.information(
                        None,
                        QCoreApplication.translate(
                            "CycloneDX", "CycloneDX - SBOM Creation"
                        ),
                        QCoreApplication.translate(
                            "CycloneDX",
                            "<p>The SBOM data was written to file <b>{0}</b>.</p>",
                        ).format(sbomFile),
                    )
                else:
                    error = str(
                        process.readAllStandardError(),
                        Preferences.getSystem("IOEncoding"),
                        "replace",
                    )
                    EricMessageBox.critical(
                        None,
                        QCoreApplication.translate(
                            "CycloneDX", "CycloneDX - SBOM Creation"
                        ),
                        QCoreApplication.translate(
                            "CycloneDX",
                            "<p>The SBOM file <b>{0}</b> could not be written.</p>"
                            "<p>Error:<br/>{1}</p>",
                        ).format(sbomFile, error),
                    )
            else:
                EricMessageBox.critical(
                    None,
                    QCoreApplication.translate(
                        "CycloneDX", "CycloneDX - SBOM Creation"
                    ),
                    QCoreApplication.translate(
                        "CycloneDX",
                        "<p>The SBOM creation process did not finish within 30s.</p>",
                    ),
                )
        else:
            EricMessageBox.critical(
                None,
                QCoreApplication.translate("CycloneDX", "CycloneDX - SBOM Creation"),
                QCoreApplication.translate(
                    "CycloneDX",
                    "<p>The SBOM creation process could not be started.</p>"
                    "<p>Reason: {0}</p>",
                ).format(process.errorString()),
            )
