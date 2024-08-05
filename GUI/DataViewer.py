from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QAction, QSplitter, QMenuBar
from PyQt5.QtCore import Qt
import numpy as np
import pyqtgraph as pg

class GraphWindow(QMainWindow):
    COLORS = ['r', 'b', 'g', 'y', 'o', 'k']
    STATUS_MERGED = 0
    STATUS_SPLIT = 1
    TYPE_MULTIPLE = 1
    TYPE_SINGLE = 0
    def __init__(self,parent, type = TYPE_SINGLE):
        super().__init__(parent)
        self.type = type
        self.plotStatus = GraphWindow.STATUS_MERGED
        self.setWindowTitle("Pressure Graph")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        if type == GraphWindow.TYPE_MULTIPLE:
            self.menu_bar = QMenuBar(self)
            self.setMenuBar(self.menu_bar)
            # Add a menu and action to split the graph
            self.view_menu = self.menu_bar.addMenu("View")
            self.split_action = QAction("Split", self)
            self.combine_action = QAction("Combine", self)
            self.split_action.triggered.connect(self.splitGraphs)
            self.combine_action.triggered.connect(self.combineGraphs)
            self.view_menu.addAction(self.split_action)
            self.view_menu.addAction(self.combine_action)

        # Create a layout for the plot widgets
        self.plot_layout = QVBoxLayout()
        self.main_layout.addLayout(self.plot_layout)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("Pressure", color="black", size="12pt")
        self.plot_layout.addWidget(self.plot_widget)

        self.plot_widgets = [self.plot_widget]
        self.y_unit = "None"
        if self.type == GraphWindow.TYPE_MULTIPLE:
            self.combine_action.setEnabled(False)

    def setYLabel(self,ylabel):
        self.y_unit = ylabel

    def updateYlabel(self,index = 0):
        self.plot_widgets[index].setLabel('left', self.y_unit, color='black', size='12pt')

    def xlabel(self, xlabel="Time (min)", index = 0):
        self.plot_widgets[index].setLabel('bottom', xlabel, color='black', size='12pt')

    def plotData(self, x=None, y=None, color ='r', index = 0, symbol='o', symbolSize=8):
        if x is None or y is None:
            x = np.linspace(0, 10, 100)
            y = np.sin(x)

        if len(self.plot_widgets) == 1:
            index = 0

        # Plot the data
        print(x,y)
        self.plot_widgets[index].plot(x, y, pen=pg.mkPen(color=color, width=2), symbol=symbol, symbolSize=symbolSize, symbolBrush=pg.mkBrush(color))
        self.updateYlabel(index=index)
        self.xlabel()

    def addLegend(self):
        self.legend = pg.LegendItem((80, 60), offset=(30, 30))
        self.legend.setParentItem(self.plot_widgets[0].graphicsItem())
        if len(self.plot_widgets) == 1:
            for i,plot in enumerate(self.plot_widgets[0].getPlotItem().items):
                self.legend.addItem(plot,f"Senor AI{i}")


    def clearGraph(self):
        for plot in self.plot_widgets:
            plot.clear()

    def closeEvent(self, event):
        if hasattr(self.parent(),"onGraphClosed"):
            self.parent().onGraphClosed()
        super().closeEvent(event)

    def combineGraphs(self):
        for i in reversed(range(self.splitter.count())):
            self.splitter.widget(i).setParent(None)
        self.splitter.setParent(None)
        self.splitter = None

        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')
        plot_widget.setTitle(f"Pressure", color="black", size="12pt")
        plot_widgets = self.plot_widgets
        self.plot_widgets = [plot_widget]
        for i,plot in enumerate(plot_widgets):
            x, y = plot.getPlotItem().items[0].getData()
            self.plotData(x, y, GraphWindow.COLORS[i])

        self.plot_layout.addWidget(plot_widget)
        self.updateYlabel()
        self.xlabel()
        self.addLegend()
        self.split_action.setEnabled(True)
        self.combine_action.setEnabled(False)


    def splitGraphs(self):


        plot_widget = self.plot_widgets[0]
        plots = plot_widget.getPlotItem().items
        print(plots)

        self.splitter = QSplitter(Qt.Vertical)
        self.plot_widgets = []

        for i in range(len(plots)):
            plot_widget = pg.PlotWidget()
            plot_widget.setBackground('w')
            plot_widget.setTitle(f"Pressure (Sensor AI{i + 1})", color="black", size="12pt")

            self.splitter.addWidget(plot_widget)
            self.plot_widgets.append(plot_widget)
            x, y = plots[i].getData()
            self.plotData(x, y, GraphWindow.COLORS[i], i)
            self.updateYlabel(i)
            self.xlabel(index=i)


        for i in range(self.plot_layout.count()):
            self.plot_layout.itemAt(i).widget().setParent(None)
        self.plot_layout.addWidget(self.splitter)
        self.split_action.setEnabled(False)
        self.combine_action.setEnabled(True)
