"""
Python Version: 3.7, 32 bit
     Last Edit: 1/31/2020
        Author: Keith Huddleston
         Email: kdhuddle@ksu.edu
"""

# -------------------------------------------------------------------------- #
# Module Imports
# -------------------------------------------------------------------------- #
import matplotlib.pyplot as plt
import numpy as np
import time

# -------------------------------------------------------------------------- #
# Class
# -------------------------------------------------------------------------- #
class controlPA:
    """ Used to control a Keithley 6487 picoammeter """

    def __init__(self, address='GPIB0::22::INSTR'):
        #  Imports modules needed for class functions
        import numpy as np
        import pyvisa
        #  Initialize NI VISA resource manager
        rm = pyvisa.ResourceManager()

        #  Check if specified address is seen by NI VISA
        if address in np.array(rm.list_resources()):
            self.connectStatus = True
        else:
            self.connectStatus = False
            print('Could not connect, is address valid?')

        #  Connect to device if address is found
        if self.connectStatus:
            self.inst = rm.open_resource(address)
            print('Connected to ' + self.inst.query('*IDN?') + '\n')

            #  Return Keithley 6487 to GPIB default settings
            self.inst.write('*RST')

    def aquireData(self, COUN=20, POIN=20):
#        self.inst.write('CURR:RANGE 200E-9')  #  Set current Range
#        time.sleep(0.05)
        self.inst.write('CURR:RANGE:AUTO OFF')
        time.sleep(0.05)
        self.inst.write('TRIG:CLE')
        time.sleep(0.05)
        self.inst.write('FORM:ELEM READ')
        time.sleep(0.05)
        self.inst.write('TRIG:COUN 20')  #  Set trigger model to take 20 readings
        time.sleep(0.05)
        self.inst.write('TRAC:POIN 20')  #  Set buffer size to 20
        time.sleep(0.05)
        self.inst.write('TRAC:FEED SENS')  #  Store raw input readings
        time.sleep(0.05)        
        self.inst.write('TRAC:FEED:CONT NEXT')  #  Start storing readings
        time.sleep(0.05)        
        self.inst.write('SYST:ZCH OFF') #  Disable zero check
        time.sleep(0.05)
        self.inst.write('INIT')  #  Trigger readings setup to SRQ on buffer full
        time.sleep(6)            #  NOTE!!! You need to give device time to record
        self.inst.write('SYST:ZCH ON') #  enable zero check
        time.sleep(0.1)
        self.inst.write('CALC3:FORM MEAN')
        time.sleep(0.05)
        return float(self.inst.query('CALC3:DATA?'))
    
    def voltageSweep(self, start, stop, step, delay=0.1):
        sweep1 = ['SOUR:VOLT:RANG ' + str(int(i)) for i in np.arange(start, stop+step, step)]
        sweep2 = ['SOUR:VOLT ' + str(int(i)) for i in np.arange(start, stop+step, step)]
        sweep3 = ['SOUR:VOLT?' for i in np.arange(start, stop+step, step)]
        for i in range(len(sweep1)):
            time.sleep(1)
            self.inst.write(sweep1[i])
            time.sleep(1)
            self.inst.write(sweep2[i])    
            time.sleep(1)
            print(self.inst.query(sweep3[i]))
            print(self.aquireData())
            
        
if __name__ == '__main__':
    pico = controlPA()
#
#    print(pico.aquireData())
#    print(pico.aquireData())
##    print(pico.aquireData())
##    print(pico.aquireData())
##    print(pico.aquireData())
#    print(pico.voltageSweep(100, 500, 50))
#
#
#    print('End of Test')