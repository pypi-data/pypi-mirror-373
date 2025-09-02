# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a specialized line edit widget for entering secrets.
"""

import enum

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QSizePolicy, QToolButton, QWidget

from eric7.EricGui import EricPixmapCache


class EricPasswordEditMode(enum.Enum):
    """
    Class defining the various modes for the password edit widget.
    """

    Password = 0
    Pin = 1
    Token = 2
    User = 255


class EricPasswordEdit(QWidget):
    """
    Class implementing a specialized line edit widget for entering secrets.

    It includes a line edit and a button to toggle the visibility of entered secret.
    The edit can be used in different modes, which mainly affect the strings shown.
    The default mode is EricPasswordEditMode.Password. When mode is
    EricPasswordEditMode.User, the strings must be given AFTER this mode was set with
    EricPasswordEdit.setMode().

    @signal editingFinished() emitted to signal the end of editing
    @signal returnPressed() emitted to signal pressing the 'Return' or 'Enter' key
    @signal textChanged(str) emitted to signal any change of the text (programmatic
        or by the user)
    @signal textEdited(str) emitted to signal changes made by the user
    @signal visibilityToggled(bool) emitted to signal a change of the secret visibility
    """

    editingFinished = pyqtSignal()
    returnPressed = pyqtSignal()
    textChanged = pyqtSignal(str)
    textEdited = pyqtSignal(str)

    visibilityToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent=parent)

        self.__buttonToolTips = {}

        self.__layout = QHBoxLayout(self)

        self.__lineEdit = QLineEdit()
        self.__lineEdit.setClearButtonEnabled(True)

        icon = QIcon()
        icon.addPixmap(EricPixmapCache.getPixmap("showPassword"), state=QIcon.State.Off)
        icon.addPixmap(EricPixmapCache.getPixmap("hidePassword"), state=QIcon.State.On)
        self.__toggleVisibilityButton = QToolButton()
        self.__toggleVisibilityButton.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.__toggleVisibilityButton.setCheckable(True)
        self.__toggleVisibilityButton.setIcon(icon)

        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)

        self.__layout.addWidget(self.__lineEdit)
        self.__layout.addWidget(self.__toggleVisibilityButton)

        self.setLayout(self.__layout)

        self.setFocusProxy(self.__lineEdit)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # establish signal-slot connections
        self.__lineEdit.editingFinished.connect(self.editingFinished)
        self.__lineEdit.returnPressed.connect(self.returnPressed)
        self.__lineEdit.textChanged.connect(self.textChanged)
        self.__lineEdit.textEdited.connect(self.textEdited)

        self.__toggleVisibilityButton.toggled.connect(self.__toggleVisibility)

        # finalize default setup (Password)
        self.setMode(EricPasswordEditMode.Password)
        self.__toggleVisibility(False)

    @pyqtSlot(bool)
    def __toggleVisibility(self, checked):
        """
        Private slot to toggle the password visibility.

        @param checked state of the visibility toggle button
        @type bool
        """
        self.__lineEdit.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.__toggleVisibilityButton.setToolTip(self.__buttonToolTips[checked])

        self.visibilityToggled.emit(checked)

    def setMode(self, mode):
        """
        Public method to set the mode of the password edit.

        @param mode mode of the edit
        @type EricPasswordEditMode
        """
        checkState = self.__toggleVisibilityButton.isChecked()

        if mode == EricPasswordEditMode.Password:
            self.__buttonToolTips = {
                True: self.tr("Press to hide the password."),
                False: self.tr("Press to show the password."),
            }
            self.__lineEdit.setToolTip(self.tr("Enter the password."))
        elif mode == EricPasswordEditMode.Pin:
            self.__buttonToolTips = {
                True: self.tr("Press to hide the pin."),
                False: self.tr("Press to show the pin."),
            }
            self.__lineEdit.setToolTip(self.tr("Enter the pin."))
        elif mode == EricPasswordEditMode.Token:
            self.__buttonToolTips = {
                True: self.tr("Press to hide the token."),
                False: self.tr("Press to show the token."),
            }
            self.__lineEdit.setToolTip(self.tr("Enter the token."))
        elif mode == EricPasswordEditMode.User:
            self.__buttonToolTips = {
                True: "",
                False: "",
            }
            self.__lineEdit.setToolTip("")

        self.__toggleVisibility(checkState)

    def setUserStrings(self, checkedToolTip="", uncheckedToolTip="", editToolTip=""):
        """
        Public method to set the strings in User mode.

        @param checkedToolTip tool tip text for the visibility button in checked
            state (defaults to "")
        @type str (optional)
        @param uncheckedToolTip tool tip text for the visibility button in unchecked
            state (defaults to "")
        @type str (optional)
        @param editToolTip tool tip text for the line edit (defaults to "")
        @type str (optional)
        """
        checkState = self.__toggleVisibilityButton.isChecked()

        self.__buttonToolTips = {
            True: checkedToolTip,
            False: uncheckedToolTip,
        }
        self.__lineEdit.setToolTip(editToolTip)

        self.__toggleVisibility(checkState)

    #######################################################################
    ## QLineEdit like interface methods
    #######################################################################

    @pyqtSlot()
    def clear(self):
        """
        Public slot to clear the line edit.
        """
        self.__lineEdit.clear()

    @pyqtSlot(str)
    def setText(self, text):
        """
        Public slot to set the text of the line edit.

        @param text text string
        @type str
        """
        self.__lineEdit.setText(text)

    def text(self):
        """
        Public method to get the entered text.

        @return text of the line edit
        @rtype str
        """
        return self.__lineEdit.text()

    def setToolTip(self, text):
        """
        Public method to set the tool tip text of the line edit.

        @param text tool tip text
        @type str
        """
        self.__lineEdit.setToolTip(text)

    def toolTip(self):
        """
        Public method to get the tool tip text of the line edit.

        @return tool tip text
        @rtype str
        """
        return self.__lineEdit.toolTip()

    def setPlaceholderText(self, text):
        """
        Public method to set the placeholder text of the line edit.

        @param text placeholder text
        @type str
        """
        self.__lineEdit.setPlaceholderText(text)

    def placeholderText(self):
        """
        Public method to get the placeholder text of the line edit.

        @return placeholder text
        @rtype str
        """
        return self.__lineEdit.placeholderText()

    @pyqtSlot()
    def selectAll(self):
        """
        Public slot to select the text of the line edit.
        """
        self.__lineEdit.selectAll()
