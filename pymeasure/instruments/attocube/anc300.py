#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from math import inf

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.instruments.attocube.adapters import AttocubeConsoleAdapter


def extract_value(reply):
    """ get_process function for the Attocube console which for numerical
    values typically return 'name = X.YZ unit'

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return reply.split('=')[1].split()[0]


def extract_float(reply):
    """ get_process function for the Attocube console to obtain a float from
    the reply

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return float(extract_value(reply))


def extract_int(reply):
    """ get_process function for the Attocube console to obtain an integer from
    the reply

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return int(extract_value(reply))


class Axis(object):
    """ Represents a single open loop axis of the Attocube ANC350

    :param axis: axis identifier, integer from 1 to 7
    :param controller: ANC300Controller instance used for the communication
    """

    serial_nr = Instrument.measurement("getser",
                                       "Serial number of the axis")

    voltage = Instrument.control(
            "getv", "setv %.3f",
            """ Amplitude of the stepping voltage in volts from 0 to 150 V. This
            property can be set. """,
            validator=strict_range, values=[0, 150],
            get_process=extract_float)

    frequency = Instrument.control(
            "getf", "setf %.3f",
            """ Frequency of the stepping motion in Hertz from 1 to 10000 Hz.
            This property can be set. """,
            validator=strict_range, values=[1, 10000],
            get_process=extract_int)

    mode = Instrument.control(
            "getm", "setm %s",
            """ Axis mode. This can be 'gnd', 'inp', 'cap', 'stp', 'off',
            'stp+', 'stp-'. Available modes depend on the actual axis model""",
            validator=strict_discrete_set,
            values=['gnd', 'inp', 'cap', 'stp', 'off', 'stp+', 'stp-'],
            get_process=extract_value)

    offset_voltage = Instrument.control(
            "geta", "seta %.3f",
            """ Offset voltage in Volts from 0 to 150 V.
            This property can be set. """,
            validator=strict_range, values=[0, 150],
            get_process=extract_float)

    output_voltage = Instrument.measurement("geto",
                                            """ Output voltage in volts.""",
                                            get_process=extract_float)

    capacity = Instrument.measurement("getc",
                                      """ Saved capacity value in nF of the
                                      axis.""",
                                      get_process=extract_float)

    stepu = Instrument.setting(
            "stepu %d",
            """ Step upwards for N steps. Mode must be 'stp' and N must be
            positive.""",
            validator=strict_range, values=[0, inf])

    stepd = Instrument.setting(
            "stepd %d",
            """ Step downwards for N steps. Mode must be 'stp' and N must be
            positive.""",
            validator=strict_range, values=[0, inf])

    def __init__(self, axis, controller):
        self.axis = str(axis)
        self.controller = controller

    def _add_axis_id(self, command):
        """ add axis id to a command string at the correct position after the
        initial command, but before a potential value

        :param command: command string
        :returns: command string with added axis id
        """
        cmdparts = command.split()
        cmdparts.insert(1, self.axis)
        return ' '.join(cmdparts)

    def ask(self, command, **kwargs):
        return self.controller.ask(self._add_axis_id(command), **kwargs)

    def write(self, command, **kwargs):
        return self.controller.write(self._add_axis_id(command), **kwargs)

    def values(self, command, **kwargs):
        return self.controller.values(self._add_axis_id(command), **kwargs)

    def stop(self):
        """ Stop any motion of the axis """
        self.write('stop')

    def move(self, steps, gnd=True):
        """ Move 'steps' steps in the direction given by the sign of the
        argument. This method will change the mode of the axis automatically
        and ground the axis on the end if 'gnd' is True. The method returns
        only when the movement is finished.

        :param steps: finite integer value of steps to be performed. A positive
        sign corresponds to upwards steps, a negative sign to downwards steps.
        :param gnd: bool, flag to decide if the axis should be grounded after
        completion of the movement
        """
        self.mode = 'stp'
        # perform the movement
        if steps > 0:
            self.stepu = steps
        elif steps < 0:
            self.stepd = abs(steps)
        else:
            pass  # do not set stepu/d to 0 since it triggers a continous move
        # wait for the move to finish
        self.write('stepw')
        if gnd:
            self.mode = 'gnd'

    def measure_capacity(self):
        """ Obtains a new measurement of the capacity. The mode of the axis
        returns to 'gnd' after the measurement.

        :returns capacity: the freshly measured capacity in nF.
        """
        self.mode = 'cap'
        # wait for the measurement to finish
        self.ask('capw')
        return self.capacity


class ANC300Controller(Instrument):
    """ Attocube ANC300 Piezo stage controller with several axes

    :param host: host address of the instrument
    :param axisnames: a list of axis names which will be used to create
                      properties with these names
    :param passwd: password for the attocube standard console
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """
    version = Instrument.measurement(
           "ver", """ Version number and instrument identification """
           )

    controllerBoardVersion = Instrument.measurement(
           "getcser", """ Serial number of the controller board """
           )

    def __init__(self, host, axisnames, passwd, **kwargs):
        if 'query_delay' not in kwargs:
            kwargs['query_delay'] = 0.05
        super(ANC300Controller, self).__init__(
            AttocubeConsoleAdapter(host, 7230, passwd, **kwargs),
            "attocube ANC300 Piezo Controller",
            includeSCPI = False,
            **kwargs
        )
        for i, axis in enumerate(axisnames):
            setattr(self, axis, Axis(i+1, self))

    def ground_all(self):
        """ Grounds all axis of the controller. """
        for attr in dir(self):
            attribute = getattr(self, attr)
            if isinstance(attribute, Axis):
                attribute.mode = 'gnd'

    def stop_all(self):
        """ Stop all movements of the axis. """
        for attr in dir(self):
            attribute = getattr(self, attr)
            if isinstance(attribute, Axis):
                attribute.stop()
