from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QGroupBox, QGridLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint


# Define main window of GUI
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Define Widgets for Plotting
        self.graph_piam = pg.PlotWidget()
        self.graph_volt = pg.PlotWidget()
        self.graph_wave = pg.PlotWidget()
        self.graph_data = pg.PlotWidget()

        # Timers for Plotting Picoammeter, Picoammeter Voltage, and Wavelength
        self.timer_piam = QtCore.QTimer()
        self.timer_volt = QtCore.QTimer()
        self.timer_wave = QtCore.QTimer()

        # Set background color of plots to White
        self.graph_piam.setBackground('w')
        self.graph_volt.setBackground('w')
        self.graph_wave.setBackground('w')

        # Set dummy variables
        self.time = list(range(100))         # 100 time points
        self.piam = [0 for _ in range(100)]  # 100 data points
        self.volt = [0 for _ in range(100)]  # 100 data points
        self.wave = [0 for _ in range(100)]  # 100 data points

        # Add grid to all plots
        self.graph_piam.showGrid(x=True, y=True)
        self.graph_volt.showGrid(x=True, y=True)
        self.graph_wave.showGrid(x=True, y=True)

        # Set Data line color
        pen = pg.mkPen(color=(255, 0, 0))
        self.piam_line = self.graph_piam.plot(self.time, self.piam, pen=pen)
        self.volt_line = self.graph_volt.plot(self.time, self.volt, pen=pen)
        self.wave_line = self.graph_wave.plot(self.time, self.wave, pen=pen)

        #  x-axis and y-axis Labels
        self.graph_piam.setLabel('bottom', 'Time [Seconds]')
        self.graph_piam.setLabel('left', 'Current [Amps]')
        self.graph_volt.setLabel('bottom', 'Time [Seconds]')
        self.graph_volt.setLabel('left', 'Voltage [V]')
        self.graph_wave.setLabel('bottom', 'Time [Seconds]')
        self.graph_wave.setLabel('left', 'Wavelength [nm]')

        #  Define GUI Layout
#        bStart = self.start_plot_button(cont_fun=True)
#        bStop = self.stop_plot_button(cont_fun=True)
#        file_name_box = QLineEdit()
#
        layout = QGridLayout()
#        layout.addWidget(bStart, 0, 0)
#        layout.addWidget(bStop, 0, 1)
#        layout.addWidget(file_name_box, 2, 0, 1, 2)
#
#        layout.addWidget(self.graph_piam, 3, 0, 1, 2)
#        layout.addWidget(self.graph_volt, 4, 0, 1, 2)
#        layout.addWidget(self.graph_wave, 5, 0, 1, 2)
        layout.addWidget(self.group_plot())
        layout.addWidget(self.group_data())
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Photo-Cathode Deposition GUI')

    def group_plot(self):
        group_box = QGroupBox('Section: Plotting')
        grid_box = QGridLayout()
        grid_box.addWidget(self.start_plot_button(cont_fun=True), 0, 0)
        grid_box.addWidget(self.stop_plot_button(cont_fun=True), 0, 1)
        grid_box.addWidget(self.graph_piam, 1, 0, 1, 2)
        grid_box.addWidget(self.graph_volt, 2, 0, 1, 2)
        grid_box.addWidget(self.graph_wave, 3, 0, 1, 2)
        grid_box.addWidget(self.start_plot_button(cont_fun=True), 4, 0, 1, 1)
        grid_box.addWidget(self.graph_data, 5, 0, 1, 2)
        group_box.setLayout(grid_box)
        return group_box
    
    def group_data(self):
        group_box = QGroupBox('Section: Data Logging')
        grid_box = QGridLayout()
        file_name_box = QLineEdit()
        grid_box.addWidget(file_name_box, 0, 0, 1, 2)
        group_box.setLayout(grid_box)
        return group_box
        
    # Updating Plot Data -----------------------------------------------------
    def update_plot_data(self):
        self.time = self.time[1:]            # Remove the first X element.
        self.time.append(self.time[-1] + 1)  # Add a new value 1 higher than the last.
        
        self.piam = self.piam[1:]         # Remove the first y element
        self.piam.append( randint(0,100)) # Add a new random value.
        self.piam_line.setData(self.time, self.piam)
        
        self.volt = self.volt[1:]         # Remove the first y element
        self.volt.append( randint(0,100)) # Add a new random value.
        self.volt_line.setData(self.time, self.volt)

        self.wave = self.wave[1:]         # Remove the first y element
        self.wave.append( randint(0,100)) # Add a new random value.
        self.wave_line.setData(self.time, self.wave)

    def cont_plot(self, timer):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()        
        
    def start_plot_button(self, cont_fun):
        btn = QPushButton('Start/Resume', self)
        if not cont_fun:
            btn.clicked.connect(self.update_plot_data)
        else:
            btn.clicked.connect(self.cont_plot)
        return btn
    
    def stop_plot(self):
        self.timer.stop()
        
    def plot_saved_data(self):
        return
        
    def stop_plot_button(self, cont_fun):
        btn = QPushButton('Pause', self)
        if not cont_fun:
            return
        else:
            btn.clicked.connect(self.stop_plot)
        return btn
    # End of Updating Plot Section -------------------------------------------


app = QtWidgets.QApplication([])
w = MainWindow()
w.show()
sys.exit(app.exec_())