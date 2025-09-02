# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a specialized dialog for entering secrets.
"""

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from eric7.EricWidgets.EricPasswordEdit import EricPasswordEdit, EricPasswordEditMode


class EricPasswordDialog(QDialog):
    """
    Class implementing a specialized dialog for entering secrets.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent=parent)

        self.resize(400, 100)
        self.setSizeGripEnabled(True)

        self.__layout = QVBoxLayout(self)

        self.__message = QLabel()
        self.__message.setWordWrap(True)

        self.__passwordEdit = EricPasswordEdit()

        self.__buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.__layout.addWidget(self.__message)
        self.__layout.addWidget(self.__passwordEdit)
        self.__layout.addWidget(self.__buttonBox)

        self.__buttonBox.accepted.connect(self.accept)
        self.__buttonBox.rejected.connect(self.reject)

        self.__passwordEdit.setFocus()

        msh = self.minimumSizeHint()
        self.resize(max(self.width(), msh.width()), msh.height())

    def setLabelText(self, text):
        """
        Public method to set the text of the message label.

        @param text message text
        @type str
        """
        self.__message.setText(text)

    def setPassword(self, password):
        """
        Public method to set the contents of the password edit.

        @param password password to be set
        @type str
        """
        self.__passwordEdit.setText(password)

    def password(self):
        """
        Public method to get the entered password.

        @return entered password
        @rtype str
        """
        return self.__passwordEdit.text()

    def setPasswordEditMode(self, mode):
        """
        Public method to set the mode of the password edit.

        @param mode mode of the edit
        @type EricPasswordEditMode
        """
        self.__passwordEdit.setMode(mode)

    def setUserStrings(self, checkedToolTip="", uncheckedToolTip="", editToolTip=""):
        """
        Public method to set the strings in User mode.

        @param checkedToolTip tool tip text for the visibility button of the password
            edit in checked state (defaults to "")
        @type str (optional)
        @param uncheckedToolTip tool tip text for the visibility button of the password
            edit in unchecked state (defaults to "")
        @type str (optional)
        @param editToolTip tool tip text for the line edit of the password edit
            (defaults to "")
        @type str (optional)
        """
        self.__passwordEdit.setUserStrings(
            checkedToolTip=checkedToolTip,
            uncheckedToolTip=uncheckedToolTip,
            editToolTip=editToolTip,
        )

    def setCancelButtonText(self, text):
        """
        Public method to set the text of the 'Cancel' button.

        @param text text for the 'Cancel' button
        @type str
        """
        self.__buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText(text)

    def setOkButtonText(self, text):
        """
        Public method to set the text of the 'Ok' button.

        @param text text of the 'Ok' button
        @type str
        """
        self.__buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText(text)


def getPassword(parent, title, label, password=""):  # secok
    """
    Function to show a dialog for entering a password.

    @param parent reference to the parent widget
    @type QWidget
    @param title title of the dialog
    @type str
    @param label message text to be shown
    @type str
    @param password password to be set (defaults to "")
    @type str (optional)
    @return tuple containing the entered password and a flag indicating that the
        'Ok' button was pressed
    @rtype tuple of (str, bool)
    """
    dlg = EricPasswordDialog(parent=parent)
    dlg.setWindowTitle(title)
    dlg.setLabelText(label)
    dlg.setPasswordEditMode(EricPasswordEditMode.Password)
    dlg.setPassword(password)

    ok = dlg.exec() == QDialog.DialogCode.Accepted
    return dlg.password(), ok


def getPin(parent, title, label, pin=""):  # secok
    """
    Function to show a dialog for entering a pin.

    @param parent reference to the parent widget
    @type QWidget
    @param title title of the dialog
    @type str
    @param label message text to be shown
    @type str
    @param pin pin to be set (defaults to "")
    @type str (optional)
    @return tuple containing the entered pin and a flag indicating that the
        'Ok' button was pressed
    @rtype tuple of (str, bool)
    """
    dlg = EricPasswordDialog(parent=parent)
    dlg.setWindowTitle(title)
    dlg.setLabelText(label)
    dlg.setPasswordEditMode(EricPasswordEditMode.Pin)
    dlg.setPassword(pin)

    ok = dlg.exec() == QDialog.DialogCode.Accepted
    return dlg.password(), ok


def getToken(parent, title, label, token=""):  # secok
    """
    Function to show a dialog for entering a token.

    @param parent reference to the parent widget
    @type QWidget
    @param title title of the dialog
    @type str
    @param label message text to be shown
    @type str
    @param token token string to be set (defaults to "")
    @type str (optional)
    @return tuple containing the entered token string and a flag indicating that the
        'Ok' button was pressed
    @rtype tuple of (str, bool)
    """
    dlg = EricPasswordDialog(parent=parent)
    dlg.setWindowTitle(title)
    dlg.setLabelText(label)
    dlg.setPasswordEditMode(EricPasswordEditMode.Token)
    dlg.setPassword(token)

    ok = dlg.exec() == QDialog.DialogCode.Accepted
    return dlg.password(), ok
