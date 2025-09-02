# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Mdule implementing the viewmanager navigation history related classes.
"""

import time

from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


@dataclass(frozen=True)
class NavigationHistoryItem:
    """
    Class defining the data structure of a navigation history entry.
    """

    filename: str
    linenumber: int


class NavigationHistory(QObject):
    """
    Class implementing the navigation history controller.

    @signal historyCleared() emitted to indicate that the history was cleared
    @signal historyItemAdded() emitted to indicate that a new entry was recorded
    @signal historyChanged() emitted to indicate a change of history
    """

    historyCleared = pyqtSignal()
    historyItemAdded = pyqtSignal()
    historyChanged = pyqtSignal()

    def __init__(self, vm, offset=5, maxEntries=100, parent=None):
        """
        Constructor

        @param vm reference to the viewmanager object
        @type ViewManager
        @param offset minimum line offset for recording (defaults to 10)
        @type int (optional)
        @param maxEntries maximum number of history entries (defaults to 100)
        @type int (optional)
        @param parent reference to the parent object (defaults to None)
        @type QObject (optional)
        """
        super().__init__(parent=parent)

        self.__backList = []
        self.__forwardList = []
        self.__currentItem = None
        self.__inGoTo = False
        self.__lastAdd = time.monotonic()

        self.__vm = vm
        self.__lineOffset = offset
        self.__maxEntries = maxEntries

    #######################################################################
    ## Methods dealing with the complete history list.
    #######################################################################

    def clear(self):
        """
        Public method to clear the history.
        """
        self.__backList.clear()
        self.__forwardList.clear()
        self.__currentItem = None

        self.historyCleared.emit()

    def count(self):
        """
        Public method to get the total number of items in the history.

        @return total number of history items
        @rtype int
        """
        return (
            len(self.__backList)
            + len(self.__forwardList)
            + (1 if self.currentItem is not None else 0)
        )

    def currentItem(self):
        """
        Public method to get the current item.

        @return current item
        @rtype NavigationHistoryItem
        """
        return self.__currentItem

    def items(self):
        """
        Public method to get the list of items currently in the history.

        @return list of all history items
        @rtype list of NavigationHistoryItem
        """
        return (
            self.__backList[:]
            + ([self.__currentItem] if self.__currentItem else [])
            + self.__forwardList[:]
        )

    def addItem(self, item):
        """
        Public method to add an item to the history and make it the current one.

        This method clears the forward history list. If the given item is
        already the current item, the addition and clearing is skipped.

        @param item item to be added
        @type NavigationHistoryItem
        """
        if self.__currentItem is None or item != self.__currentItem:
            self.__forwardList.clear()
            if self.__currentItem is not None:
                if (
                    self.__currentItem.filename == item.filename
                    and self.__currentItem.linenumber == 1
                    and item.linenumber != 1
                    and time.monotonic() - self.__lastAdd < 0.5  # 500 ms
                ):
                    # just replace the current entry
                    self.__currentItem = item
                    return

                self.__backList.append(self.__currentItem)
            self.__currentItem = item
            self.__lastAdd = time.monotonic()

            self.historyItemAdded.emit()

            self.__adjustHistorySize()

    def goToItem(self, item):
        """
        Public method to set the current item to the specified item in the history
        and go to that location.

        @param item item to make the current one
        @type NavigationHistoryItem
        """
        if item is None:
            return

        if item in self.__backList:
            # go back
            self.__forwardList.insert(0, self.__currentItem)
            while self.__backList:
                itm = self.__backList.pop(-1)  # get last item
                if itm == item:
                    break
                else:
                    self.__forwardList.insert(0, itm)  # insert it into the forward list
        elif item in self.__forwardList:
            # go forward
            self.__backList.append(self.__currentItem)
            while self.__forwardList:
                itm = self.__forwardList.pop(0)  # get first item
                if itm == item:
                    break
                else:
                    self.__backList.append(itm)
        else:
            # Oops, the item is not in either list or is the current one already.
            return

        self.__currentItem = item
        self.__inGoTo = True
        self.__vm.openSourceFile(
            fn=self.__currentItem.filename, lineno=self.__currentItem.linenumber
        )
        self.historyChanged.emit()
        self.__inGoTo = False

    @pyqtSlot(str, int)
    def recordPosition(self, filename, linenumber):
        """
        Public slot to record the given position.

        This method records the given filename and line number with the history,
        if that is not already the current position. Recording a new position will
        clear the forward history list. Given positions will only be recorded,
        if the filename is different to the current one or the line number is
        different by a configurable offset (default 10).

        @param filename name of the file
        @type str
        @param linenumber line number of the cursor
        @type int
        """
        if not self.__inGoTo and (
            self.__currentItem is None
            or filename != self.__currentItem.filename
            or not (
                self.__currentItem.linenumber - self.__lineOffset
                < linenumber
                < self.__currentItem.linenumber + self.__lineOffset
            )
        ):
            navItem = NavigationHistoryItem(filename=filename, linenumber=linenumber)
            if navItem in self.__backList or navItem in self.__forwardList:
                # treat it like an explicit selection via the navigation menus
                self.goToItem(navItem)
            else:
                # add a new record
                self.addItem(navItem)

    def setMinimumLineOffset(self, offset):
        """
        Public method to set minimum line offset to record a new entry.

        @param offset line offset value
        @type int
        """
        self.__lineOffset = offset

    def setMaximumSize(self, maxEntries):
        """
        Public method to set the maximum number of entries to be kept.

        @param maxEntries maximum number of entries
        @type int
        """
        self.__maxEntries = maxEntries
        self.__adjustHistorySize()

    def __adjustHistorySize(self):
        """
        Private method to adjust the size of the kept history.
        """
        cnt = self.count()
        if cnt > self.__maxEntries:
            delta = cnt - self.__maxEntries
            if delta < len(self.__backList):
                del self.__backList[:delta]
                self.historyChanged.emit()
            else:
                self.clear()

    #######################################################################
    ## Methods dealing with the back navigation list.
    #######################################################################

    @pyqtSlot()
    def back(self):
        """
        Public slot to set the current item to be the previous one and move to
        that place.
        """
        if self.__backList:
            self.__forwardList.insert(0, self.__currentItem)
            self.__currentItem = self.__backList.pop(-1)

            self.__vm.openSourceFile(
                fn=self.__currentItem.filename, lineno=self.__currentItem.linenumber
            )
            self.historyChanged.emit()

    def backItem(self):
        """
        Public method to get the item before the current item.

        @return item before the current item
        @rtype NavigationHistoryItem
        """
        return self.__backList[-1] if self.__backList else None

    def backItems(self):
        """
        Public method to get the list of items in the backwards history list.

        @return copy of backwards history items
        @rtype list of NavigationHistoryItem
        """
        return self.__backList[:]

    def canGoBack(self):
        """
        Public method to check, if backward movement is possible.

        @return flag indicating possible backward movement
        @rtype bool
        """
        return bool(self.__backList)

    #######################################################################
    ## Methods dealing with the forward navigation list.
    #######################################################################

    @pyqtSlot()
    def forward(self):
        """
        Public slot to set the current item to be the next one and move to
        that place.
        """
        if self.__forwardList:
            self.__backList.append(self.__currentItem)
            self.__currentItem = self.__forwardList.pop(0)

            self.__vm.openSourceFile(
                fn=self.__currentItem.filename, lineno=self.__currentItem.linenumber
            )
            self.historyChanged.emit()

    def forwardItem(self):
        """
        Public method to get the item after the current item.

        @return item after the current item
        @rtype NavigationHistoryItem
        """
        return self.__forwardList[0] if self.__forwardList else None

    def forwardItems(self):
        """
        Public method to get the list of items in the forwards history list.

        @return copy of forwards history items
        @rtype list of NavigationHistoryItem
        """
        return self.__forwardList[:]

    def canGoForward(self):
        """
        Public method to check, if forward movement is possible.

        @return flag indicating possible forward movement
        @rtype bool
        """
        return bool(self.__forwardList)
