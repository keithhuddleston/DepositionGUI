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
                            QCheckBox, QComboBox
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
        self.graph_piam = pg.PlotWidget()
        self.graph_volt = pg.PlotWidget()  # Not Currently Used
        self.graph_wave = pg.PlotWidget()  # Not Currently Used
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
        self.time = [time.time() for i in range(100)]  # 100 time points
        self.piam = [0 for i in range(100)]            # 100 data points
        self.volt = [0 for i in range(100)]            # 100 data points
        self.wave = [0 for i in range(100)]            # 100 data points

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
        self.mono_conn_fun()
        self.pico_conn_fun()

        # Group: Data Logging ------------------------------------------------
        self.file_name = ''
        self.save_data_flag = False

        # Group: Data and Plottings ------------------------------------------
        self.volt_val = 0
        self.wave_val = 0
        self.curr_ran = 0

        #  Define GUI Layout
        layout = QGridLayout()

        layout.addWidget(self.group_conn(), 0, 0, 1, 2)
        layout.addWidget(self.group_data(), 1, 0, 1, 2)
        layout.addWidget(self.group_cont(), 2, 0, 1, 2)
        layout.addWidget(self.group_plot(), 0, 2, 4, 6)
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
        wavelength = [str(int(i)) for i in np.arange(start, stop+step, step)]
        for i in range(len(sweep)):
            print(sweep[i])
            self.wave_val = str(str(wavelength[i]))
            self.wave_val_line.setText(self.wave_val)
            self.mono.write(sweep[i])
            self.update_data()
        return

    def volt_para_set_btn(self):
        btn = QPushButton('Run', self)
        btn.clicked.connect(self.volt_para_set_fun)
        return btn

    def volt_para_set_fun(self):
        start = int(self.volt_line_edit_start.text())
        stop  = int(self.volt_line_edit_stop.text())
        step  = int(self.volt_line_edit_step.text())
        sweep1 = ['SOUR:VOLT:RANG ' + str(int(i)) for i in np.arange(start, stop+step, step)]
        sweep2 = ['SOUR:VOLT ' + str(int(i)) for i in np.arange(start, stop+step, step)]
        sweep3 = ['SOUR:VOLT?' for i in np.arange(start, stop+step, step)]
        voltage = [str(int(i)) for i in np.arange(start, stop+step, step)]
        for i in range(len(sweep1)):
            print(sweep1[i])
            print(sweep2[i])
            self.volt_val = voltage[i]
            self.pico_inst.inst.write(sweep1[i])
            time.sleep(0.1)
            self.pico_inst.inst.write(sweep2[i])
            time.sleep(0.1)
            print(self.pico_inst.inst.query(sweep3[i]))
            self.update_data()
            self.volt_val_line.setText(voltage[i])
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

        self.shutterCB = QComboBox()
        self.shutterCB.addItem('Open')
        self.shutterCB.addItem('Close')
        self.shutterCB.activated[str].connect(self.mono_shutter)

        self.wave_line_edit = QLineEdit()
        grid_box.addWidget(self.wave_line_edit, 0, 1)
        grid_box.addWidget(self.wave_set_btn(), 0, 2)
        grid_box.addWidget(self.shutterCB, 0, 3)
        group_box.setLayout(grid_box)
        return group_box

    def wave_set_btn(self):
        btn = QPushButton('Set', self)
        btn.clicked.connect(self.wave_set_fun)
        return btn

    def mono_shutter(self, text):
        print(b'SHUTTER '+str.encode(text[0]))
        self.mono.write(b'SHUTTER '+str.encode(text[0]))

    def wave_set_fun(self):
        print(b'GOWAVE '+str.encode(self.wave_line_edit.text()))
        self.wave_val = str(self.wave_line_edit.text())
        self.wave_val_line.setText(self.wave_val)
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

        self.comboBox = QComboBox()

        self.comboBox.addItem('2E-2')
        self.comboBox.addItem('2E-3')
        self.comboBox.addItem('2E-4')
        self.comboBox.addItem('2E-5')
        self.comboBox.addItem('2E-6')
        self.comboBox.addItem('2E-7')
        self.comboBox.addItem('2E-8')
        self.comboBox.addItem('2E-9')
        self.comboBox.activated[str].connect(self.CURR_RANG)

        grid_box.addWidget(QLabel('CURR:RANG'), 0, 3)
        grid_box.addWidget(self.comboBox, 0, 4)
        group_box.setLayout(grid_box)
        return group_box

    def volt_set_btn(self):
        btn = QPushButton('Set', self)
        btn.clicked.connect(self.volt_set_fun) 
        return btn

    def CURR_RANG(self, text):
        print('CURR:RANG '+text)
        self.pico_inst.inst.write('CURR:RANG '+text)
        self.curr_ran = text
        print(self.pico_inst.inst.query('CURR:RANG?'))

    def volt_set_fun(self):
        print('SOUR:VOLT '+str(int(self.volt_line_edit.text())))
        c = 'SOUR:VOLT:RANG ' + str(int(self.volt_line_edit.text()))
        self.pico_inst.inst.write(c)
        self.pico_inst.inst.write(c)
        time.sleep(0.5)
        c = 'SOUR:VOLT ' + str(int(self.volt_line_edit.text()))
        self.pico_inst.inst.write(c)
        time.sleep(0.5)
        print(self.pico_inst.inst.query('SOUR:VOLT?'))
        self.volt_val = str(self.volt_line_edit.text())
        self.volt_val_line.setText(self.volt_val)
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
        self.pico_inst = controlPA()
        if self.pico_inst.connectStatus:
            self.pico_conn_status.setText('Connected')
        else:
            self.pico_conn_status.setText('Failed to Connect to Device')
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
        return

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
        if self.pico_inst.connectStatus:
            new_piam = self.pico_inst.aquireData()
        else:
            new_piam = 0
        self.piam.append(new_piam) # Add a new random value.

        self.volt = self.volt[1:]         # Remove the first y element
        new_volt = self.volt_val
        self.volt.append(new_volt) # Add a new random value.

        self.wave = self.wave[1:]  # Remove the first y element
        new_wave = self.wave_val
        self.wave.append(new_wave) # Add a new random value

        if self.save_data_flag:
            print('saving')
            self.F.write(str(new_time) + '\t' + str(new_piam) + '\t' + str(new_volt) + '\t' + str(new_wave) + '\t' + str(self.curr_ran) + '\n')
            self.F.flush()

    # ------------------------------------------------------------------------
    # Group: Plotting Functions
    # ------------------------------------------------------------------------
    def update_plot_data(self):
        self.piam_line.setData(self.time, self.piam)
        self.volt_line.setData(self.time, self.volt)
        self.wave_line.setData(self.time, self.wave)

    def cont_plot(self, timer):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(7*1000)
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
        grid_box.addWidget(self.start_plot_button(cont_fun=True), 0, 0, 1, 2)
        grid_box.addWidget(self.stop_plot_button(cont_fun=True), 0, 2, 1, 2)
        grid_box.addWidget(self.graph_piam, 1, 0, 1, 4)
        grid_box.addWidget(QLabel('Wavelength: '), 2, 0)
        self.wave_val_line = QLabel(str(self.wave_val))
        self.volt_val_line = QLabel(str(self.volt_val))
        grid_box.addWidget(self.wave_val_line, 2, 1)
        grid_box.addWidget(QLabel('Voltage: '), 2, 2)
        grid_box.addWidget(self.volt_val_line, 2, 3)
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
