"""
Python Version: 3.7, 32 bit
     Last Edit: 1/31/2020
        Author: Keith Huddleston
         Email: kdhuddle@ksu.edu
"""

# -------------------------------------------------------------------------- #
# Imports
# -------------------------------------------------------------------------- #
import matplotlib.pyplot as plt
import numpy as np
import ctypes

# -------------------------------------------------------------------------- #
# Class
# -------------------------------------------------------------------------- #
class controlMC:
    """ Used to Read and Write to Oriel Cornerstone 260 Monochromator """

    def __init__(self, \
            libDict=r'C:\Users\Dep Chamber\Desktop\meas_python_scripts\DLL', \
            libName=r'ODevice.dll'):
        #  Imports modules needed for class functions
        import numpy as np
        import ctypes
        import os

        #  Import Oriel Control .dll Library
        fd = os.getcwd()  #  File Directory
        os.chdir(libDict)
        self.lib = ctypes.CDLL(libName)
        os.chdir(fd)

        #  Open Oriel Device, defaults to first Oriel device found
        self.connectStatus = self.lib.odev_open()

        # .odev_open function returns 1 if Oriel device is opened
        if self.connectStatus > 0:
            print('\nConnected to Monochromator\n')
        else:
            print('\nCould not connect to Monochromator\n')

    def write(self, message):
        """ Send Message to Oriel Cornerstone 260 Monochromator.  See MCS130
            document for the command reference summary

            Input:

              message: essage sent to monochromator.

                 wait: Time to wait between each message

            Output: None
        """
        assert self.connectStatus, \
        'ERROR, not connected to any devices'

        assert type(message) == bytes, 'Input must be type bytes'

        message = ctypes.create_string_buffer(message, 256)

        self.lib.odev_write(message)

        return

    def close(self):
        """ Stop communication with monochromator
        """
        self.lib.odev_close()
        return
    
# -------------------------------------------------------------------------- #
# Testing
# -------------------------------------------------------------------------- #
if __name__ == '__main__':
    mono = controlMC()
    sweep = [b'GOWAVE ' + str.encode(str(int(i))) for i in np.arange(325, 700+25, 25)]
    print('start sweep')
    for wave in sweep:
        print(wave)
        mono.write(wave)
    print('End')