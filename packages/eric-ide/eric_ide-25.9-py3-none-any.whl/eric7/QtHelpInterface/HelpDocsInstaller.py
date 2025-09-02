# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a thread class populating and updating the QtHelp
documentation database.
"""

import datetime
import pathlib

from PyQt6.QtCore import QMutex, QThread, pyqtSignal
from PyQt6.QtHelp import QHelpEngineCore

from eric7.Globals import getConfig


class HelpDocsInstaller(QThread):
    """
    Class implementing the worker thread populating and updating the QtHelp
    documentation database.

    @signal errorMessage(str) emitted, if an error occurred during
        the installation of the documentation
    @signal docsInstalled(bool) emitted after the installation has finished
    """

    errorMessage = pyqtSignal(str)
    docsInstalled = pyqtSignal(bool)

    def __init__(self, collection):
        """
        Constructor

        @param collection full pathname of the collection file
        @type str
        """
        super().__init__()

        self.__abort = False
        self.__collection = collection
        self.__mutex = QMutex()

    def stop(self):
        """
        Public slot to stop the installation procedure.
        """
        if not self.isRunning():
            return

        self.__mutex.lock()
        self.__abort = True
        self.__mutex.unlock()
        self.wait()

    def installDocs(self):
        """
        Public method to start the installation procedure.
        """
        self.start(QThread.Priority.LowPriority)

    def run(self):
        """
        Public method executed by the thread.
        """
        engine = QHelpEngineCore(self.__collection)
        changes = False

        changes |= self.__installEric7Doc(engine)
        engine = None
        del engine
        self.docsInstalled.emit(changes)

    def __installEric7Doc(self, engine):
        """
        Private method to install/update the eric help documentation.

        @param engine reference to the help engine
        @type QHelpEngineCore
        @return flag indicating success
        @rtype bool
        """
        versionKey = "eric7_ide"
        info = engine.customValue(versionKey, "")
        lst = info.split("|")

        dt = None
        if len(lst) and lst[0]:
            dt = datetime.datetime.fromisoformat(lst[0])

        qchFile = ""
        if len(lst) == 2:
            qchFile = lst[1]

        docsPath = pathlib.Path(getConfig("ericDocDir")) / "Help"

        files = list(docsPath.glob("*.qch"))
        if not files:
            engine.setCustomValue(versionKey, "|")
            return False

        for f in files:
            if f.name == "source.qch":
                namespace = QHelpEngineCore.namespaceName(str(f.resolve()))
                if not namespace:
                    continue

                if (
                    dt is not None
                    and namespace in engine.registeredDocumentations()
                    and (
                        datetime.datetime.fromtimestamp(
                            f.stat().st_mtime, tz=datetime.timezone.utc
                        )
                        == dt
                    )
                    and qchFile == str(f.resolve())
                ):
                    return False

                if namespace in engine.registeredDocumentations():
                    engine.unregisterDocumentation(namespace)

                if not engine.registerDocumentation(str(f.resolve())):
                    self.errorMessage.emit(
                        self.tr(
                            """<p>The file <b>{0}</b> could not be"""
                            """ registered. <br/>Reason: {1}</p>"""
                        ).format(f, engine.error())
                    )
                    return False

                engine.setCustomValue(
                    versionKey,
                    datetime.datetime.fromtimestamp(
                        f.stat().st_mtime, tz=datetime.timezone.utc
                    ).isoformat()
                    + "|"
                    + str(f.resolve()),
                )
                return True

        return False
