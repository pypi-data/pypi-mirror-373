# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the MicroPython diagram widget based on QtGraphs.
"""

import contextlib
import csv
import os
import time

from PyQt6.QtCore import QObject, Qt, QUrl, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGraphs import QGraphsTheme, QLineSeries, QValueAxis
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from eric7 import Preferences
from eric7.EricGui import EricPixmapCache
from eric7.EricWidgets import EricMessageBox


class MicroPythonLineGraphWidgetItem(QObject):
    """
    Class implementing an object embedding the QML GraphsView.

    @signal lineSeriesChanged() signal to notify the graphs view about a change
        of the list of line series
    @signal graphsThemeChanged() signal to notify the graphs view about a theme change
    @signal xAxisChanged() signal to notify the graphs view about a change of the x-axis
    @signal yAxisChanged() signal to notify the graphs view about a change of the y-axis
    """

    lineSeriesChanged = pyqtSignal()
    graphsThemeChanged = pyqtSignal()
    xAxisChanged = pyqtSignal()
    yAxisChanged = pyqtSignal()

    QmlPropertyName = "lineGraph"
    QmlSource = """
import QtQuick
import QtGraphs

Item {
    id: mainView
    width: 1280
    height: 720

    GraphsView {
        id: graphsView
        anchors.fill: parent

        marginBottom: 2
        marginLeft: 2
        marginRight: 10
        marginTop: 10

        theme: lineGraph.graphsTheme
        seriesList: lineGraph.lineSeries
        axisX: lineGraph.xAxis
        axisY: lineGraph.yAxis
    }
}
"""

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent object (defaults to None)
        @type QObject (optional)
        """
        super().__init__(parent=parent)

        self.__lineSeries = []

        self.__maxPointsCount = 100
        self.__pointsCount = 0

        self.__xAxis = QValueAxis()
        self.__xAxis.setTickInterval(1)
        self.__xAxis.setSubTickCount(4)
        self.__xAxis.setLabelDecimals(-1)

        self.__yAxis = QValueAxis()
        self.__yAxis.setTickInterval(1)
        self.__yAxis.setSubTickCount(4)
        self.__yAxis.setLabelDecimals(-1)

        self.__updateAxis()

        self.__graphsTheme = QGraphsTheme()
        self.preferencesChanged()

    @pyqtSlot()
    def preferencesChanged(self):
        """
        Public slot handling a change of configuration entries.
        """
        # 1. graph theme
        theme = Preferences.getMicroPython("GraphColorTheme")
        if theme >= len(QGraphsTheme.Theme):
            # set to default for an invalid value
            self.__graphsTheme.setTheme(QGraphsTheme.Theme.QtGreen)
        else:
            self.__graphsTheme.setTheme(QGraphsTheme.Theme(theme))

        # 2. graph scheme
        scheme = Preferences.getMicroPython("GraphColorScheme")
        if scheme >= len(QGraphsTheme.ColorScheme):
            # set to default for an invalid value
            self.__graphsTheme.setColorScheme(QGraphsTheme.ColorScheme.Automatic)
        else:
            self.__graphsTheme.setColorScheme(QGraphsTheme.ColorScheme(scheme))

    ############################################################################
    ## Property definitions to interact with the QML view
    ############################################################################

    def getGraphsTheme(self):
        """
        Public method to get a reference to the graphs theme object.

        @return reference to the graphs theme object
        @rtype QGraphsTheme
        """
        return self.__graphsTheme

    def getLineSeries(self):
        """
        Public method to get the list of line series objects to be shown by the
        QML view.

        @return list of line series objects
        @rtype QLineSeries
        """
        return self.__lineSeries

    def getXAxis(self):
        """
        Public method to get a reference to the x-axis object.

        @return reference to the x-axis object
        @rtype QValueAxis
        """
        return self.__xAxis

    def getYAxis(self):
        """
        Public method to get a reference to the y-axis object.

        @return reference to the y-axis object
        @rtype QValueAxis
        """
        return self.__yAxis

    graphsTheme = pyqtProperty(
        QGraphsTheme, fget=getGraphsTheme, notify=graphsThemeChanged, final=True
    )
    lineSeries = pyqtProperty(
        list, fget=getLineSeries, notify=lineSeriesChanged, final=True
    )
    xAxis = pyqtProperty(QValueAxis, fget=getXAxis, notify=xAxisChanged, final=True)
    yAxis = pyqtProperty(QValueAxis, fget=getYAxis, notify=yAxisChanged, final=True)

    ############################################################################
    ## Method to attach this interface object to a QQuick widget.
    ############################################################################

    def setWidget(self, widget):
        """
        Public method to associate this QML object with a given QQuick widget.

        @param widget reference to the embedding QQuick widget
        @type QQuickWidget
        """
        context = widget.engine().rootContext()
        context.setContextProperty(MicroPythonLineGraphWidgetItem.QmlPropertyName, self)
        widget.setSource(
            QUrl(
                "data:application/x-qml;utf-8,{0}".format(
                    MicroPythonLineGraphWidgetItem.QmlSource
                )
            )
        )

    ############################################################################
    ## Methods implementing special behavior below.
    ############################################################################

    def __updateAxis(self):
        """
        Private method to adjust the axis ranges to the line values.
        """
        xPoints = (
            [p.x() for p in self.__lineSeries[0].points()] if self.__lineSeries else []
        )
        minX = xPoints[0] if bool(xPoints) else 0.0
        maxX = (
            max(xPoints[-1], self.__maxPointsCount)
            if bool(xPoints)
            else self.__maxPointsCount
        )
        self.__xAxis.setRange(minX, maxX)
        self.__xAxis.setTickInterval((maxX - minX) / 4.0)

        yPoints = []
        for lineSeries in self.__lineSeries:
            yPoints += [p.y() for p in lineSeries.points()]
        minY = min(yPoints) if bool(yPoints) else 0.0
        maxY = max(yPoints) if bool(yPoints) else 1.0
        self.__yAxis.setRange(minY, maxY)
        self.__yAxis.setTickInterval((maxY - minY) / 4.0)

    def __adjustLineSeriesLength(self):
        """
        Private method to adjust the line series to the maximum number of points
        set via the top level widget.
        """
        for lineSeries in self.__lineSeries:
            if lineSeries.count() > self.__maxPointsCount:
                lineSeries.removeMultiple(0, lineSeries.count() - self.__maxPointsCount)

    @pyqtSlot(int)
    def setMaxPointsCount(self, value):
        """
        Public slot to handle a change of the maximum number of points to be shown.

        @param value maximum number of points
        @type int
        """
        self.__maxPointsCount = value
        self.__adjustLineSeriesLength()
        self.__updateAxis()

    def addData(self, values):
        """
        Public method to add a tuple of values to the graph.

        It ensures there are the required number of line series, adds the data
        to the line series and updates the range of the chart so the chart
        displays nicely.

        @param values tuple containing the data to be added
        @type tuple of int or float
        """
        self.__adjustLineSeriesLength()

        if len(values) > len(self.__lineSeries):
            # adjust the number of available lines to the length of the data
            while len(values) > len(self.__lineSeries):
                self.__lineSeries.append(QLineSeries())
            self.lineSeriesChanged.emit()

        for value, line in zip(values, self.__lineSeries):
            line.append(self.__pointsCount, value)
        self.__pointsCount += 1

        self.__updateAxis()

    @pyqtSlot()
    def clear(self):
        """
        Public slot to clear the graph and reset it.
        """
        for lineSeries in self.__lineSeries:
            lineSeries.clear()
        self.__pointsCount = 0

        self.__updateAxis()

    @pyqtSlot(bool)
    def setGridVisible(self, visible):
        """
        Public slot to set the grid visibility.

        @param visible flag indicating the grid visibility
        @type bool
        """
        self.__graphsTheme.setGridVisible(visible)

    @pyqtSlot(bool)
    def setSubGridVisible(self, visible):
        """
        Public slot to set the sub-grid visibility.

        @param visible flag indicating the sub-grid visibility
        @type bool
        """
        self.__xAxis.setSubGridVisible(visible)
        self.__yAxis.setSubGridVisible(visible)


class MicroPythonLineGraphWidget(QQuickWidget):
    """
    Class implementing a widget embedding the line graph object.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (defaults to None)
        @type QWidget (optional)
        """
        super().__init__(parent=parent)

        self.__lineGraphItem = MicroPythonLineGraphWidgetItem()
        self.__lineGraphItem.setWidget(self)

        self.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)

    def widgetItem(self):
        """
        Public method to get a reference to the graph view interface item.

        @return reference to the graph view interface item
        @rtype MicroPythonLineGraphWidgetItem
        """
        return self.__lineGraphItem

    def shutdown(self):
        """
        Public method to perform some shutdown actions.
        """
        self.setSource(QUrl())


class MicroPythonGraphWidget(QWidget):
    """
    Class implementing the MicroPython diagram widget based on QtGraphs.

    @signal dataFlood emitted to indicate, that too much data is received
    """

    dataFlood = pyqtSignal()

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)

        self.__layout = QHBoxLayout()
        self.__layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.__layout)

        self.__lineGraphWidget = MicroPythonLineGraphWidget()
        self.__lineGraphWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.__layout.addWidget(self.__lineGraphWidget)

        self.__verticalLayout = QVBoxLayout()
        self.__verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.__layout.addLayout(self.__verticalLayout)

        self.__buttonsLayout = QHBoxLayout()

        self.__saveButton = QToolButton(self)
        self.__saveButton.setIcon(EricPixmapCache.getIcon("fileSave"))
        self.__saveButton.setToolTip(self.tr("Press to save the raw data"))
        self.__saveButton.clicked.connect(self.on_saveButton_clicked)
        self.__buttonsLayout.addWidget(self.__saveButton)

        self.__eraseButton = QToolButton(self)
        self.__eraseButton.setIcon(EricPixmapCache.getIcon("editDelete"))
        self.__eraseButton.setToolTip(
            self.tr("Press to clear the graph and delete the raw data")
        )
        self.__eraseButton.clicked.connect(self.__eraseData)
        self.__buttonsLayout.addWidget(self.__eraseButton)

        self.__verticalLayout.addLayout(self.__buttonsLayout)
        self.__verticalLayout.setAlignment(
            self.__buttonsLayout, Qt.AlignmentFlag.AlignHCenter
        )

        spacerItem = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.__verticalLayout.addItem(spacerItem)

        self.__gridCheckBox = QCheckBox(self.tr("Show Grid"))
        self.__gridCheckBox.setChecked(True)
        self.__verticalLayout.addWidget(self.__gridCheckBox)

        self.__subGridCheckBox = QCheckBox(self.tr("Show Subgrid"))
        self.__subGridCheckBox.setChecked(True)
        self.__verticalLayout.addWidget(self.__subGridCheckBox)

        self.__maxXLayout = QHBoxLayout()

        label = QLabel(self.tr("max. X:"))
        self.__maxXLayout.addWidget(label)

        self.__maxX = 100
        self.__maxXSpinBox = QSpinBox()
        self.__maxXSpinBox.setMinimum(100)
        self.__maxXSpinBox.setMaximum(1000)
        self.__maxXSpinBox.setSingleStep(100)
        self.__maxXSpinBox.setToolTip(
            self.tr("Enter the maximum number of data points to be plotted.")
        )
        self.__maxXSpinBox.setValue(self.__maxX)
        self.__maxXSpinBox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__maxXLayout.addWidget(self.__maxXSpinBox)

        self.__verticalLayout.addLayout(self.__maxXLayout)

        self.__inputBuffer = []  # holds the data to be checked for plotable data
        self.__rawData = []  # holds the raw data
        self.__dirty = False
        self.__flooded = False  # flag indicating a data flood

        self.__lineGraphWidget.widgetItem().setMaxPointsCount(self.__maxX)
        self.__maxXSpinBox.valueChanged.connect(
            self.__lineGraphWidget.widgetItem().setMaxPointsCount
        )
        self.__gridCheckBox.toggled.connect(
            self.__lineGraphWidget.widgetItem().setGridVisible
        )
        self.__subGridCheckBox.toggled.connect(
            self.__lineGraphWidget.widgetItem().setSubGridVisible
        )

    @pyqtSlot()
    def preferencesChanged(self):
        """
        Public slot to apply changed preferences.
        """
        self.__lineGraphWidget.widgetItem().preferencesChanged()

    @pyqtSlot(bytes)
    def processData(self, data):
        """
        Public slot to process the raw data.

        It takes raw bytes, checks the data for a valid tuple of ints or
        floats and adds the data to the graph. If the the length of the bytes
        data is greater than 1024 then a dataFlood signal is emitted to ensure
        eric can take action to remain responsive.

        @param data raw data received from the connected device via the main
            device widget
        @type bytes
        """
        # flooding guard
        if self.__flooded:
            return

        if len(data) > 1024:
            self.__flooded = True
            self.dataFlood.emit()
            return

        # disable the inputs while processing data
        self.__saveButton.setEnabled(False)
        self.__maxXSpinBox.setEnabled(False)

        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        self.__inputBuffer.append(data)

        # check if the data contains a Python tuple containing numbers (int
        # or float) on a single line
        inputBytes = b"".join(self.__inputBuffer)
        lines = inputBytes.splitlines(True)
        for line in lines:
            if not line.endswith(b"\n"):
                # incomplete line (last line); skip it
                break

            line = line.strip()
            if line.startswith(b"(") and line.endswith(b")"):
                # it may be a tuple we are interested in
                rawValues = [val.strip() for val in line[1:-1].split(b",")]
                values = []
                for raw in rawValues:
                    with contextlib.suppress(ValueError):
                        values.append(int(raw))
                        # ok, it is an integer
                        continue
                    try:
                        values.append(float(raw))
                    except ValueError:
                        # it is not an int or float, ignore it
                        continue
                if values:
                    self.__addData(tuple(values))

        self.__inputBuffer = []
        if lines[-1] and not lines[-1].endswith(b"\n"):
            # Append any left over bytes for processing next time data is
            # received.
            self.__inputBuffer.append(lines[-1])

        # re-enable the inputs
        self.__saveButton.setEnabled(True)
        self.__maxXSpinBox.setEnabled(True)

    def __addData(self, values):
        """
        Private method to add a tuple of values to the graph.

        @param values tuple containing the data to be added
        @type tuple of int or float
        """
        # store incoming data to be able to dump it as CSV upon request
        self.__rawData.append(values)
        self.__dirty = True

        self.__lineGraphWidget.widgetItem().addData(values)

    @pyqtSlot()
    def __eraseData(self):
        """
        Private slot to erase the graph and the stored raw data.
        """
        yes = not self.__dirty or EricMessageBox.yesNo(
            self,
            self.tr("Clear Graph"),
            self.tr("""Shall the graph and the raw data really be erased?"""),
        )
        if yes:
            # 1. clear the raw data
            self.__rawData.clear()
            self.__dirty = False

            # 2. remove all plotted lines and associated data
            self.__lineGraphWidget.widgetItem().clear()

    @pyqtSlot()
    def on_saveButton_clicked(self):
        """
        Private slot to save the raw data to a CSV file.
        """
        self.saveData()

    def hasData(self):
        """
        Public method to check, if the chart contains some valid data.

        @return flag indicating valid data
        @rtype bool
        """
        return len(self.__rawData) > 0

    def isDirty(self):
        """
        Public method to check, if the chart contains unsaved data.

        @return flag indicating unsaved data
        @rtype bool
        """
        return self.hasData() and self.__dirty

    def saveData(self):
        """
        Public method to save the dialog's raw data.

        @return flag indicating success
        @rtype bool
        """
        baseDir = (
            Preferences.getMicroPython("MpyWorkspace")
            or Preferences.getMultiProject("Workspace")
            or os.path.expanduser("~")
        )
        dataDir = os.path.join(baseDir, "data_capture")

        if not os.path.exists(dataDir):
            os.makedirs(dataDir)

        # save the raw data as a CSV file
        fileName = "{0}.csv".format(time.strftime("%Y%m%d-%H%M%S"))
        fullPath = os.path.join(dataDir, fileName)
        try:
            with open(fullPath, "w") as csvFile:
                csvWriter = csv.writer(csvFile)
                csvWriter.writerows(self.__rawData)

            self.__dirty = False
            return True
        except OSError as err:
            EricMessageBox.critical(
                self,
                self.tr("Save Graph Data"),
                self.tr(
                    """<p>The graph data could not be saved into file"""
                    """ <b>{0}</b>.</p><p>Reason: {1}</p>"""
                ).format(fullPath, str(err)),
            )
            return False

    def shutdown(self):
        """
        Public method to perform some shutdown actions.
        """
        self.__lineGraphWidget.shutdown()
