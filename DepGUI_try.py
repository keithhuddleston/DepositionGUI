"""
Python Version: 3.7, 32 bit
     Last Edit: 1/31/2020
        Author: Keith Huddleston
         Email: kdhuddle@ksu.edu
"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QPushButton, \
                            QLineEdit, QGroupBox, QGridLayout, QLabel,      \
                            QCheckBox
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint

import numpy as np
import time

# Custom Modules
from monoChromUtility import controlMC
from picoAmmUtility import controlPA

# ----------------------------------------------------------------------------
# Define the Main Window of the GUI
# ----------------------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Define Widgets for Plotting
        self.graph_main = pg.PlotWidget()
        self.plot_piam = self.graph_main.plotItem
        self.plot_volt = pg.ViewBox()
        self.plot_wave = pg.ViewBox()
        
        # Testing
        self.plot_piam.setLabels(left='Current [Amps]')
        self.plot_piam.showAxis('right')
        self.plot_piam.scene().addItem(self.plot_volt)
        self.plot_piam.getAxis('right').linkToView(self.plot_volt)
        self.plot_volt.setXLink(self.plot_piam)
        self.plot_piam.getAxis('right').setLabel('axis2', color='#0000ff')
        self.plot_wave = pg.ViewBox()
        self.wave_axis = pg.AxisItem('right')
        self.plot_piam.layout.addItem(self.wave_axis, 2, 3)
        self.plot_piam.scene().addItem(self.plot_wave)
        self.wave_axis.linkToView(self.plot_wave)
        self.plot_wave.setXLink(self.plot_piam)
        self.wave_axis.setZValue(-10000)
        self.wave_axis.setLabel('axis 3', color='#ff0000')


        self.update_views()
        self.plot_piam.vb.sigResized.connect(self.update_views)                                
        
        # End Testing
        
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
        self.time = [time.time() for _ in range(10)] # 100 time points
        self.piam = [0 for _ in range(10)]           # 100 data points
        self.volt = [0 for _ in range(10)]           # 100 data points
        self.wave = [0 for _ in range(10)]           # 100 data points

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

        # Group: Connection --------------------------------------------------
        self.mono_conn_status = QLabel('Not Connected')
        self.pico_conn_status = QLabel('Not Connected')

        # Group: Data Logging ------------------------------------------------
        self.file_name = ''
        self.save_data_flag = False

        # Group: Data and Plottings ------------------------------------------
        self.volt_val = 0
        self.wave_val = 0

        #  Define GUI Layout
        layout = QGridLayout()

        layout.addWidget(self.group_conn(), 0, 0, 1, 2)
        layout.addWidget(self.group_data(), 1, 0, 1, 2)
        layout.addWidget(self.group_cont(), 2, 0, 1, 2)
        layout.addWidget(self.group_plot(), 0, 2, 4, 2)
        layout.addWidget(self.group_para(), 3, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle('Photo-Cathode Deposition GUI')


    # ------------------------------------------------------------------------
    # Group: Parametric Studies
    # ------------------------------------------------------------------------

    # Main Widget used to control parametric studies for MC and PA
    def group_para(self):
        group_box = QGroupBox('Section: Parametric Studies')
        grid_box = QGridLayout()
        grid_box.addWidget(self.group_sub_para_mono(), 0, 0)
        grid_box.addWidget(self.group_sub_para_pico(), 1, 0)
        group_box.setLayout(grid_box)
        return group_box

    # Widget to control monochromator wavelength parametric studies
    def group_sub_para_mono(self):
        # Edit Lines for starting stopping and step size for MC wavelength
        self.wave_line_edit_start = QLineEdit()
        self.wave_line_edit_stop = QLineEdit()
        self.wave_line_edit_step = QLineEdit()
        # Group box and layout for the MC parametric studies section
        group_box = QGroupBox('Monochromator')
        grid_box = QGridLayout()
        grid_box.addWidget(QLabel('Start'), 0, 0)
        grid_box.addWidget(QLabel('Stop '), 0, 2)
        grid_box.addWidget(QLabel('Step '), 0, 4)
        grid_box.addWidget(self.wave_line_edit_start, 0, 1)
        grid_box.addWidget(self.wave_line_edit_stop, 0, 3)
        grid_box.addWidget(self.wave_line_edit_step, 0, 5)
        grid_box.addWidget(self.wave_para_set_btn(), 0, 6)
        group_box.setLayout(grid_box)
        return group_box

    # Widget to control picoammeter voltage parametric studies
    def group_sub_para_pico(self):
        # Edit Lines for starting stopping and step size for PA voltage
        self.volt_line_edit_start = QLineEdit()
        self.volt_line_edit_stop = QLineEdit()
        self.volt_line_edit_step = QLineEdit()
        # Group box and layout for the PA parametric studies section
        group_box = QGroupBox('Picoammeter')
        grid_box = QGridLayout()
        grid_box.addWidget(QLabel('Start'), 0, 0)
        grid_box.addWidget(QLabel('Stop '), 0, 2)
        grid_box.addWidget(QLabel('Step '), 0, 4)
        grid_box.addWidget(self.volt_line_edit_start, 0, 1)
        grid_box.addWidget(self.volt_line_edit_stop, 0, 3)
        grid_box.addWidget(self.volt_line_edit_step, 0, 5)
        grid_box.addWidget(self.volt_para_set_btn(), 0, 6)
        group_box.setLayout(grid_box)
        return group_box

    # Button to run parametric study defined in QLineEdits for wavelength
    def wave_para_set_btn(self):
        btn = QPushButton('Run', self)
        btn.clicked.connect(self.wave_para_set_fun)
        return btn

    # Function run when wave_para_set_btn is pressed
    def wave_para_set_fun(self):
        start = int(self.wave_line_edit_start.text())
        stop  = int(self.wave_line_edit_stop.text())
        step  = int(self.wave_line_edit_step.text())
        sweep = [b'GOWAVE ' + str.encode(str(int(i))) for i in np.arange(start, stop+step, step)]
        for wave in sweep:
            print(wave)
            self.mono.write(wave)
        return

    def volt_para_set_btn(self):
        btn = QPushButton('Run', self)
        btn.clicked.connect(self.wave_para_set_fun)
        return btn

    def volt_para_set_fun(self):
        start = int(self.wave_line_edit_start.text())
        stop  = int(self.wave_line_edit_stop.text())
        step  = int(self.wave_line_edit_step.text())
        sweep = [b'GOWAVE ' + str.encode(str(int(i))) for i in np.arange(start, stop+step, step)]
        for wave in sweep:
            print(wave)
            self.mono.write(wave)
        return
    
    # ------------------------------------------------------------------------
    # Group: Control Functions
    # ------------------------------------------------------------------------
    def group_cont(self):
        group_box = QGroupBox('Section: Device Control')
        grid_box = QGridLayout()
        grid_box.addWidget(self.group_mono_cont(), 0, 0)
        grid_box.addWidget(self.group_pico_cont(), 0, 1)
        group_box.setLayout(grid_box)
        return group_box

    # Monochromator
    def group_mono_cont(self):
        group_box = QGroupBox('Monochromator')
        grid_box = QGridLayout()
        grid_box.addWidget(QLabel('Wavelength:'), 0, 0)

        self.wave_line_edit = QLineEdit()
        grid_box.addWidget(self.wave_line_edit, 0, 1)
        grid_box.addWidget(self.wave_set_btn(), 0, 2)

        group_box.setLayout(grid_box)
        return group_box

    def wave_set_btn(self):
        btn = QPushButton('Set', self)
        btn.clicked.connect(self.wave_set_fun)
        return btn

    def wave_set_fun(self):
        print(b'GOWAVE '+str.encode(self.wave_line_edit.text()))
        self.mono.write(b'GOWAVE '+str.encode(self.wave_line_edit.text()))
        return

    # Picoammeter
    def group_pico_cont(self):
        group_box = QGroupBox('Picoammeter')
        grid_box = QGridLayout()
        grid_box.addWidget(QLabel('Voltage:'), 0, 0)
        
        self.volt_line_edit = QLineEdit()
        
        grid_box.addWidget(self.volt_line_edit, 0, 1)
        grid_box.addWidget(self.volt_set_btn(), 0, 2)
        
        group_box.setLayout(grid_box)
        return group_box
    
    def volt_set_btn(self):
        btn = QPushButton('Set', self)
        btn.clicked.connect(self.volt_set_fun)        
        return btn
    
    def volt_set_fun(self):
        return
    
    # ------------------------------------------------------------------------
    # Group: Connection Functions
    # ------------------------------------------------------------------------
    def mono_conn_btn(self):
        btn = QPushButton('Connect', self)
        btn.clicked.connect(self.mono_conn_fun)
        return btn

    def pico_conn_btn(self):
        btn = QPushButton('Connect', self)
        btn.clicked.connect(self.pico_conn_fun)
        return btn

    def mono_conn_fun(self):
        self.mono = controlMC()
        if self.mono.connectStatus > 0:
            self.mono_conn_status.setText('Connected')
        else:
            self.mono_conn_status.setText('Failed to Connect to Device')
        return

    def pico_conn_fun(self):
        self.pico_conn_status.setText('Connected')
        return

    def group_conn(self):
        group_box = QGroupBox('Section: Device Connection')
        grid_box = QGridLayout()
        grid_box.addWidget(QLabel('Monochromator:'), 0, 0)
        grid_box.addWidget(QLabel('Picoammeter:  '), 1, 0)
        grid_box.addWidget(self.mono_conn_btn(), 0, 1)
        grid_box.addWidget(self.pico_conn_btn(), 1, 1)
        grid_box.addWidget(QLabel('Monochromator Status:'), 0, 3)
        grid_box.addWidget(QLabel('Picoammeter Status:  '), 1, 3)
        grid_box.addWidget(self.mono_conn_status, 0, 4)
        grid_box.addWidget(self.pico_conn_status, 1, 4)
        group_box.setLayout(grid_box)
        return group_box
    
    # ------------------------------------------------------------------------
    # Group: Data Logging
    # ------------------------------------------------------------------------
    def name_set_btn(self):
        btn = QPushButton('Set', self)
        btn.clicked.connect(self.name_set_fun)
        return btn
    
    def name_set_fun(self):
        self.file_name = self.file_name_box.text()
        return
    
    def create_file_btn(self):
        btn = QPushButton('Create Data File', self)
        btn.clicked.connect(self.create_file_fun)
        return btn
    
    def create_file_fun(self):
        self.name_data_plot.setText('Saving data to file: '+self.file_name)
        self.F = open(self.file_name, 'w')
        self.save_data_flag = True
        return btn
    
    def group_data(self):
        group_box = QGroupBox('Section: Data Logging')
        grid_box = QGridLayout()
        self.file_name_box = QLineEdit()
        grid_box.addWidget(QLabel('File Name:'), 0, 0)
        grid_box.addWidget(self.file_name_box, 0, 1)
        grid_box.addWidget(self.name_set_btn(),0, 2)
        grid_box.addWidget(self.create_file_btn(),1, 0, 1, 3)
        group_box.setLayout(grid_box)
        return group_box
    
    def update_data(self):
        self.time = self.time[1:]            # Remove the first X element.
        new_time = time.time()
        self.time.append(new_time)  # Add a new value 1 higher than the last.
                
        self.piam = self.piam[1:]         # Remove the first y element
        new_piam = randint(0,100)
        self.piam.append(new_piam) # Add a new random value.
        
        self.volt = self.volt[1:]         # Remove the first y element
        new_volt = self.volt_val
        self.volt.append(new_volt) # Add a new random value.
        
        self.wave = self.wave[1:]  # Remove the first y element
        new_wave = self.wave_val
        self.wave.append(new_wave) # Add a new random value
        
        if self.save_data_flag:
            self.F.write(str(new_time) + '\t' + str(new_piam) + '\t' + str(new_volt) + '\t' + str(new_wave) + '\n')
        
    # ------------------------------------------------------------------------
    # Group: Plotting Functions
    # ------------------------------------------------------------------------
    def update_views(self):
        ## view has resized; update auxiliary views to match
        self.plot_volt.setGeometry(self.plot_piam.vb.sceneBoundingRect())
        self.plot_wave.setGeometry(self.plot_piam.vb.sceneBoundingRect())  
        
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.plot_volt.linkedViewChanged(self.plot_piam.vb, self.plot_volt.XAxis)
        self.plot_wave.linkedViewChanged(self.plot_piam.vb, self.plot_wave.XAxis)
        
    def update_plot_data(self):        
#        self.plot_piam.setData(self.time, self.piam)
        self.plot_piam.addItem(pg.PlotCurveItem(self.time, self.piam, pen='w'))
        self.plot_volt.addItem(pg.PlotCurveItem(self.time, self.volt, pen='b'))
        self.plot_wave.addItem(pg.PlotCurveItem(self.time, self.wave, pen='r'))

    def cont_plot(self, timer):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_data)
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
    
    def group_plot(self):
        self.name_data_plot = QLabel('Not Saving Data')
        group_box = QGroupBox('Section: Plotting')
        grid_box = QGridLayout()
        grid_box.addWidget(self.start_plot_button(cont_fun=True), 0, 0)
        grid_box.addWidget(self.stop_plot_button(cont_fun=True), 0, 1)
        grid_box.addWidget(self.graph_piam, 1, 0, 1, 2)
        grid_box.addWidget(self.graph_volt, 2, 0, 1, 2)
        grid_box.addWidget(self.graph_wave, 3, 0, 1, 2)
        grid_box.addWidget(self.start_plot_button(cont_fun=True), 4, 0, 1, 1)
        grid_box.addWidget(self.name_data_plot, 4, 1)
        grid_box.addWidget(self.graph_main, 5, 0, 1, 2)
        group_box.setLayout(grid_box)
        return group_box
    # End of Updating Plot Section -------------------------------------------


# ----------------------------------------------------------------------------
# Run GUI here if main file
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setStyle('Windows')
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
