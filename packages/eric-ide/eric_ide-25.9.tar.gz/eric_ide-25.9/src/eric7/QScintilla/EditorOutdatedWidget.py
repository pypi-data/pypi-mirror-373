# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a widget to warn the user when a file loaded in the editor was
modified externally.
"""

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget

from eric7.EricWidgets.EricApplication import ericApp

from .Ui_EditorOutdatedWidget import Ui_EditorOutdatedWidget


class EditorOutdatedWidget(QWidget, Ui_EditorOutdatedWidget):
    """
    Class implementing a widget to warn the user when a file loaded in the editor was
    modified externally.

    @signal activateAutoReload() emitted to indicate that the automatic reloading of
        the editor should be activated
    @signal showDiff() emitted to indicate to show the difference between the externally
        modified file and the current editor text
    @signal reloadFile() emitted to ask the editor to reload the file
    @signal ignoreChanges() emitted to tell the editor to ignore the current and all
        further modifications
    """

    StyleSheetTemplate = "QLabel {{ background: {0}; }}"
    BackgroundColors = {
        "dark": {
            "info": "#8c9ca5",
            "warning": "#c68400",
        },
        "light": {
            "info": "#cae2ef",
            "warning": "#ffd889",
        },
    }

    activateAutoReload = pyqtSignal()
    showDiff = pyqtSignal()
    reloadFile = pyqtSignal()
    ignoreChanges = pyqtSignal()

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent)
        self.setupUi(self)

        self.autoReloadButton.clicked.connect(self.activateAutoReload)
        self.diffButton.clicked.connect(self.showDiff)
        self.reloadButton.clicked.connect(self.reloadFile)
        self.ignoreButton.clicked.connect(self.ignoreChanges)

    def setMessage(self, message, messageType):
        """
        Public method to set the message text and type to be shown.

        @param message message text
        @type str
        @param messageType message type ('info' or 'warning')
        @type str
        """
        self.messageLabel.setText(message)

        colorType = "dark" if ericApp().usesDarkPalette() else "light"
        try:
            color = EditorOutdatedWidget.BackgroundColors[colorType][messageType]
        except KeyError:
            # default color is 'info'
            color = EditorOutdatedWidget.BackgroundColors[colorType]["info"]
        if ericApp().styleSheet():
            self.setStyleSheet(EditorOutdatedWidget.StyleSheetTemplate.format(color))
        else:
            self.setAutoFillBackground(True)
            pal = self.palette()
            pal.setColor(QPalette.ColorRole.Window, QColor(color))
            self.setPalette(pal)

    @pyqtSlot()
    def hide(self):
        """
        Public slot to hide the widget.
        """
        if self.styleSheet():
            self.setStyleSheet("")

        super().hide()
