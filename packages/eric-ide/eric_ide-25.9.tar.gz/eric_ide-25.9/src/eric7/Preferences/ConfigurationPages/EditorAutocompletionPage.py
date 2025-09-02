# -*- coding: utf-8 -*-

# Copyright (c) 2006 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Editor Autocompletion configuration page.
"""

from eric7 import Preferences

from .ConfigurationPageBase import ConfigurationPageBase
from .Ui_EditorAutocompletionPage import Ui_EditorAutocompletionPage


class EditorAutocompletionPage(ConfigurationPageBase, Ui_EditorAutocompletionPage):
    """
    Class implementing the Editor Autocompletion configuration page.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.setupUi(self)
        self.setObjectName("EditorAutocompletionPage")

        # set initial values
        # 'General' group
        self.acCaseSensitivityCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionCaseSensitivity")
        )
        self.acReplaceWordCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionReplaceWord")
        )
        self.acReversedCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionReversedList")
        )
        self.acLinesSlider.setValue(Preferences.getEditor("AutoCompletionMaxLines"))
        self.acCharSlider.setValue(Preferences.getEditor("AutoCompletionMaxChars"))

        # 'Automatic completion enabled' group
        self.acEnabledGroupBox.setChecked(
            Preferences.getEditor("AutoCompletionEnabled")
        )
        self.acThresholdSlider.setValue(
            Preferences.getEditor("AutoCompletionThreshold")
        )
        self.acTimeoutSpinBox.setValue(Preferences.getEditor("AutoCompletionTimeout"))
        self.noAcCommentsCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionDisabledInComments")
        )
        self.noAcStringsCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionDisabledInStrings")
        )

        # 'Plug In Behavior' group
        self.acScintillaCheckBox.setChecked(
            Preferences.getEditor("AutoCompletionScintillaOnFail")
        )
        self.acWatchdogDoubleSpinBox.setValue(
            Preferences.getEditor("AutoCompletionWatchdogTime") / 1000.0
        )

        # 'Completions Cache' group
        self.acCacheGroup.setChecked(
            Preferences.getEditor("AutoCompletionCacheEnabled")
        )
        self.acCacheSizeSpinBox.setValue(
            Preferences.getEditor("AutoCompletionCacheSize")
        )
        self.acCacheTimeSpinBox.setValue(
            Preferences.getEditor("AutoCompletionCacheTime")
        )

    def setMode(self, displayMode):
        """
        Public method to perform mode dependent setups.

        @param displayMode mode of the configuration dialog
        @type ConfigurationMode
        """
        from ..ConfigurationDialog import ConfigurationMode

        if displayMode in (ConfigurationMode.SHELLMODE,):
            self.pluginGroupBox.hide()
            self.acCacheGroup.hide()

    def save(self):
        """
        Public slot to save the Editor Autocompletion configuration.
        """
        # 'General' group
        Preferences.setEditor(
            "AutoCompletionCaseSensitivity", self.acCaseSensitivityCheckBox.isChecked()
        )
        Preferences.setEditor(
            "AutoCompletionReplaceWord", self.acReplaceWordCheckBox.isChecked()
        )
        Preferences.setEditor(
            "AutoCompletionReversedList", self.acReversedCheckBox.isChecked()
        )
        Preferences.setEditor("AutoCompletionMaxLines", self.acLinesSlider.value())
        Preferences.setEditor("AutoCompletionMaxChars", self.acCharSlider.value())

        # 'Automatic completion enabled' group
        Preferences.setEditor(
            "AutoCompletionEnabled", self.acEnabledGroupBox.isChecked()
        )
        Preferences.setEditor("AutoCompletionThreshold", self.acThresholdSlider.value())
        Preferences.setEditor("AutoCompletionTimeout", self.acTimeoutSpinBox.value())
        Preferences.setEditor(
            "AutoCompletionDisabledInComments", self.noAcCommentsCheckBox.isChecked()
        )
        Preferences.setEditor(
            "AutoCompletionDisabledInStrings", self.noAcStringsCheckBox.isChecked()
        )

        # 'Plug In Behavior' group
        Preferences.setEditor(
            "AutoCompletionScintillaOnFail", self.acScintillaCheckBox.isChecked()
        )
        Preferences.setEditor(
            "AutoCompletionWatchdogTime", self.acWatchdogDoubleSpinBox.value() * 1000
        )

        # 'Completions Cache' group
        Preferences.setEditor(
            "AutoCompletionCacheEnabled", self.acCacheGroup.isChecked()
        )
        Preferences.setEditor(
            "AutoCompletionCacheSize", self.acCacheSizeSpinBox.value()
        )
        Preferences.setEditor(
            "AutoCompletionCacheTime", self.acCacheTimeSpinBox.value()
        )


def create(_dlg):
    """
    Module function to create the configuration page.

    @param _dlg reference to the configuration dialog (unused)
    @type ConfigurationDialog
    @return reference to the instantiated page
    @rtype ConfigurationPageBase
    """
    page = EditorAutocompletionPage()
    return page
