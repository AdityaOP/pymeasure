"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from pymeasure.instruments import Instrument, RangeException
from time import sleep
import numpy as np


class LakeShore425(Instrument):
    """ Represents the LakeShore 425 Gaussmeter and provides
    a high-level interface for interacting with the instrument
    
    To allow user access to the LakeShore 425 Gaussmeter in Linux, create the file:
    /etc/udev/rules.d/52-lakeshore425.rules, with contents:    
    
    SUBSYSTEMS=="usb",ATTRS{idVendor}=="1fb9",ATTRS{idProduct}=="0401",MODE="0666",SYMLINK+="lakeshore425"
        
    Then reload the udev rules with:
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    The device will be accessible through /dev/lakeshore425 
    
    """

    UNIT_VALUES = ('Gauss', 'Tesla', 'Oersted', 'Ampere/meter')
    GAUSS, TESLA, OERSTED, AMP_METER = UNIT_VALUES
    
    def __init__(self, port):
        super(LakeShore425, self).__init__(
            LakeShoreUSBAdapter(port),
            "LakeShore 425 Gaussmeter",
        )
        self.add_control("range", "RANGE?", "RANGE %d")
        
    def setAutoRange(self):
        """ Sets the field range to automatically adjust """
        self.write("AUTO")
        
    @property
    def field(self):
        """ Returns the field given the units being used """
        return self.values("RDGFIELD?")
        
    def setDC(self, wideBand=True):
        """ Sets up a steady-state (DC) measurement of the field """
        if wideBand:
            self.setMode(1, 0, 1)
        else:
            self.setMode(1, 0, 2)
    
    def setAC(self, wideBand=True):
        """ Sets up a measurement of an oscillating (AC) field """
        if wideBand:
            self.setMode(2, 1, 1)
        else:
            self.setMode(2, 1, 2)
            
    def setMode(self, mode, filter, band):
        """ Provides access to directly setting the mode, filter, and
        bandwidth settings
        """
        self.write("RDGMODE %d,%d,%d" % (mode, filter, band))
            
    def getMode(self):
        """ Returns a tuple of the mode settings """
        return tuple(self.ask("RDGMODE?").split(','))
            
    @property
    def unit(self):
        """ Returns the full name of the unit in use as a string """
        return LakeShore425.UNIT_VALUES[int(self.ask("UNIT?"))-1]
    @unit.setter
    def unit(self, value):
        """ Sets the units from the avalible: Gauss, Tesla, Oersted, and
        Ampere/meter to be called as a string
        """
        if value in LakeShore425.UNIT_VALUES:
            self.write("UNIT %d" % (LakeShore425.UNIT_VALUES.index(value)+1))
        else:
            raise Exception("Invalid unit provided to LakeShore 425")
        
    def zeroProbe(self):
        """ Initiates the zero field sequence to calibrate the probe """
        self.write("ZPROBE")
        
    def measure(self, points, hasAborted=lambda:False, delay=1e-3):
        """Returns the mean and standard deviation of a given number
        of points while blocking
        """
        data = np.zeros(points, dtype=np.float32)
        for i in range(points):
            if hasAborted():
                break
            data[i] = self.field
            sleep(delay)
        return data.mean(), data.std()

