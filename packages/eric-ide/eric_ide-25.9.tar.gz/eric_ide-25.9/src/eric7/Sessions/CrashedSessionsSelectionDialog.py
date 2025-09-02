# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a dialog to show a list of existing crash session files.
"""

import contextlib
import json
import os
import time

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QListWidgetItem,
)

from eric7.EricWidgets import EricMessageBox

from .Ui_CrashedSessionsSelectionDialog import Ui_CrashedSessionsSelectionDialog


class CrashedSessionsSelectionDialog(QDialog, Ui_CrashedSessionsSelectionDialog):
    """
    Class implementing a dialog to show a list of existing crash session files.
    """

    def __init__(self, sessionFiles, deleteMode=False, parent=None):
        """
        Constructor

        @param sessionFiles list of crash session file names
        @type list of str
        @param deleteMode flag indicating the delete mode (defaults to False)
        @type bool (optional)
        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        self.crashedSessionsList.itemDoubleClicked.connect(self.accept)
        self.crashedSessionsList.itemActivated.connect(self.accept)
        self.crashedSessionsList.itemSelectionChanged.connect(self.__updateButtonStates)

        for sessionFile in sessionFiles:
            self.__addSessionFileEntry(sessionFile)

        self.__deleteMode = deleteMode
        if deleteMode:
            self.setWindowTitle(self.tr("Clean Crash Sessions"))
            self.messageLabel.setText(
                self.tr(
                    "These crash session files were found. Select the ones to be"
                    " deleted."
                )
            )
            self.crashedSessionsList.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
            )
            self.removeButton.hide()
        else:
            self.setWindowTitle(self.tr("Found Crash Sessions"))
            self.messageLabel.setText(
                self.tr(
                    "These crash session files were found. Select the one to open."
                    " Select 'Cancel' to not open a crash session."
                )
            )

        self.__updateButtonStates()

    @pyqtSlot()
    def __updateButtonStates(self):
        """
        Private method to update the enabled state of the buttons.
        """
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            bool(self.crashedSessionsList.selectedItems())
        )
        self.removeButton.setEnabled(bool(self.crashedSessionsList.selectedItems()))

    def __addSessionFileEntry(self, sessionFile):
        """
        Private method to read the given session file and add a list entry for it.

        @param sessionFile file name of the session to be read
        @type str
        """
        if os.path.exists(sessionFile):
            try:
                with open(sessionFile, "r") as f:
                    jsonString = f.read()
                sessionDict = json.loads(jsonString)
            except (OSError, json.JSONDecodeError) as err:
                EricMessageBox.critical(
                    None,
                    self.tr("Read Crash Session"),
                    self.tr(
                        "<p>The crash session file <b>{0}</b> could not be read.</p>"
                        "<p>Reason: {1}</p>"
                    ).format(sessionFile, str(err)),
                )
                os.remove(sessionFile)
                return

            mtime = os.path.getmtime(sessionFile)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            if sessionDict["Project"]:
                labelText = self.tr(
                    "{0}\nTimestamp: {1}\nProject: {2}",
                    "Crash Session, Timestamp, Project Path",
                ).format(sessionFile, timestamp, sessionDict["Project"])
            else:
                labelText = self.tr(
                    "{0}\nTimestamp: {1}", "Crash Session, Timestamp"
                ).format(sessionFile, timestamp)
            itm = QListWidgetItem(labelText, self.crashedSessionsList)
            itm.setData(Qt.ItemDataRole.UserRole, sessionFile)

    @pyqtSlot()
    def on_removeButton_clicked(self):
        """
        Private slot to remove the selected crash session files.
        """
        for itm in self.crashedSessionsList.selectedItems():
            crashSession = itm.data(Qt.ItemDataRole.UserRole)
            with contextlib.suppress(OSError):
                os.remove(crashSession)
            self.crashedSessionsList.takeItem(self.crashedSessionsList.row(itm))
            del itm

    def getSelectedCrashSession(self):
        """
        Public method to get the selected crash session file name.

        @return file name of the selected crash session
        @rtype str
        """
        selectedItems = self.crashedSessionsList.selectedItems()

        if selectedItems:
            return selectedItems[0].data(Qt.ItemDataRole.UserRole)
        else:
            return None

    def getSelectedCrashSessions(self):
        """
        Public method to get the selected crash session file names.

        @return file names of the selected crash sessions
        @rtype list of str
        """
        selectedItems = self.crashedSessionsList.selectedItems()

        if selectedItems:
            return [itm.data(Qt.ItemDataRole.UserRole) for itm in selectedItems]
        else:
            return []
