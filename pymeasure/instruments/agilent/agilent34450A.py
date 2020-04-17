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

import re
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


def _conf_parser(conf_values):
    """
    Parse the string of configuration parameters read from Agilent34450A with
    command ":configure?" and returns a list of parameters.

    Use cases:

    ['"CURR +1.000000E-01', '+1.500000E-06"']   ** Obtained from Instrument.measurement or Instrument.control
    '"CURR +1.000000E-01,+1.500000E-06"'        ** Obtained from Instrument.ask

    becomes

    ["CURR", +1000000E-01, +1.500000E-06]
    """
    # If not already one string, get one string

    if isinstance(conf_values, list):
        one_long_string = ', '.join(map(str, conf_values))
    else:
        one_long_string = conf_values

    # Split string in elements
    list_of_elements = re.split('["\s,]', one_long_string)

    # Eliminate empty string elements
    list_without_empty_elements = list(filter(lambda v: v != '', list_of_elements))

    # Convert numbers from str to float, where applicable
    for i, v in enumerate(list_without_empty_elements):
        try:
            list_without_empty_elements[i] = float(v)
        except Exception:
            pass

    return list_without_empty_elements


class Agilent34450A(Instrument):
    """
    Represent the HP/Agilent/Keysight 34450A and related multimeters.

    #TODO: Complete documentation, add implementation example.
    """

    # Implementation based on current keithley2000 implementation.

    # TODO: Verify that all docstrings indicate both the possible numerical values and MAX, MIN,
    #  and DEF as supported param inputs.

    # TODO: Update docstring, add capacitance
    mode = Instrument.control(
        ":CONF?", ":CONF:%s",
        """ A string property that controls the configuration mode for measurements,
        which can take the values: :code:'current' (DC), :code:'current ac',
        :code:'voltage' (DC),  :code:'voltage ac', :code:'resistance' (2-wire),
        :code:'resistance 4W' (4-wire), :code:'frequency', :code:'continuity',
        :code:'diode', and :code:'temperature'. """,
        validator=strict_discrete_set,
        values=['CURR', 'CURR:DC', 'CURR:AC', 'VOLT', 'VOLT:DC', 'VOLT:AC',
                'RES', 'FRES', 'FREQ', 'CONT', 'DIOD', 'TEMP', 'CAP'],
        get_process=_conf_parser
    )

    # TODO: Consider making individual control methods private to force access
    #  through configure_xxxxx methods.
    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(":READ?",
                                     """ Reads a DC current measurement in Amps, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    current_ac = Instrument.measurement(":READ?",
                                        """ Reads an AC current measurement in Amps, based on the
                                        active :attr:`~.Agilent34450A.mode`. """
                                        )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %s",
        """ A property that controls the DC current range in
        Amps, which can take values 100E-6, 1E-3, 10E-3, 100E-3, 1, 10, 
        as well as MIN (100 uA), DEF (100 mA), and MAX (10 A).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-6, 1E-3, 10E-3, 100E-3, 1, 10, "MIN", "DEF", "MAX"]
    )
    current_auto_range = Instrument.control(
        ":SENS:CURR:RANG:AUTO?", ":SENS:CURR:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for DC current. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    current_resolution = Instrument.control(
        ":SENS:CURR:RES?", ":SENS:CURR:RES %s",
        """ A property that controls the resolution in the DC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (3.00E-5). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %s",
        """ A property that controls the AC current range in
        Amps, which can take values 10E-3, 100E-3, 1, 10, as well as MIN (10 mA), 
        MAX (10 A), and DEF (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10E-3, 100E-3, 1, 10, "MIN", "MAX", "DEF"]
    )
    current_ac_auto_range = Instrument.control(
        ":SENS:CURR:AC:RANG:AUTO?", ":SENS:CURR:AC:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC current. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    current_ac_resolution = Instrument.control(
        ":SENS:CURR:AC:RES?", ":SENS:CURR:AC:RES %s",
        """ An property that controls the resolution in the AC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN (1.50E-6), MAX (3.00E-5), and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(":READ?",
                                     """ Reads a DC voltage measurement in Volts, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    voltage_ac = Instrument.measurement(":READ?",
                                        """ Reads an AC voltage measurement in Volts, based on the
                                        active :attr:`~.Agilent34450A.mode`. """
                                        )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %s",
        """ A property that controls the DC voltage range in
        Volts, which can take values 100E-3, 1, 10, 100, 1000, 
        as well as MIN, MAX, and DEF (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 1000, "MAX", "MIN", "DEF"]
    )
    voltage_auto_range = Instrument.control(
        ":SENS:VOLT:RANG:AUTO?", ":SENS:VOLT:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for DC voltage. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    voltage_resolution = Instrument.control(
        ":SENS:VOLT:RES?", ":SENS:VOLT:RES %s",
        """ A property that controls the resolution in the DC voltage
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %s",
        """ A property that controls the AC voltage range in
        Volts, which can take values 100E-3, 1, 10, 100, 750, 
        as well as MIN, MAX, and DEF (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 750, "MAX", "MIN", "DEF"]
    )
    voltage_ac_auto_range = Instrument.control(
        ":SENS:VOLT:AC:RANG:AUTO?", ":SENS:VOLT:AC:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC voltage. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    voltage_ac_resolution = Instrument.control(
        ":SENS:VOLT:AC:RES?", ":SENS:VOLT:AC:RES %s",
        """ A property that controls the resolution in the AC voltage
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(":READ?",
                                        """ Reads a resistance measurement in Ohms for 2-wire 
                                        configuration, based on the active 
                                        :attr:`~.Agilent34450A.mode`. """
                                        )
    resistance_4W = Instrument.measurement(":READ?",
                                           """ Reads a resistance measurement in Ohms for 
                                           4-wire configuration, based on the active 
                                           :attr:`~.Agilent34450A.mode`. """
                                           )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %s",
        """ A property that controls the 2-wire resistance range
        in Ohms, which can take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, 
        as well as MIN, MAX, and DEF (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_auto_range = Instrument.control(
        ":SENS:RES:RANG:AUTO?", ":SENS:RES:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for 2-wire resistance. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    resistance_resolution = Instrument.control(
        ":SENS:RES:RES?", ":SENS:RES:RES %s",
        """ A property that controls the resolution in the 2-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    resistance_4W_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %s",
        """ A property that controls the 4-wire resistance range
        in Ohms, which can take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, 
        as well as MIN, MAX, and DEF (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_4W_auto_range = Instrument.control(
        ":SENS:FRES:RANG:AUTO?", ":SENS:FRES:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for 4-wire resistance. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    resistance_4W_resolution = Instrument.control(
        ":SENS:FRES:RES?", ":SENS:FRES:RES %s",
        """ A property that controls the resolution in the 4-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(":READ?",
                                       """ Reads a frequency measurement in Hz, based on the
                                       active :attr:`~.Agilent34450A.mode`. """
                                       )
    frequency_current_range = Instrument.control(
        ":SENS:FREQ:CURR:RANG?", ":SENS:FREQ:CURR:RANG:AUTO 0;:SENS:FREQ:CURR:RANG %s",
        """ A property that controls the current range in Amps for frequency on AC current
        measurements, which can take values 10E-3, 100E-3, 1, 10, as well as MIN, 
        MAX, and DEF (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10E-3, 100E-3, 1, 10, "MIN", "MAX", "DEF"]
    )
    frequency_current_auto_range = Instrument.control(
        ":SENS:FREQ:CURR:RANG:AUTO?", ":SENS:FREQ:CURR:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC current in frequency measurements. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    frequency_voltage_range = Instrument.control(
        ":SENS:FREQ:VOLT:RANG?", ":SENS:FREQ:VOLT:RANG:AUTO 0;:SENS:FREQ:VOLT:RANG %s",
        """ A property that controls the voltage range in Volts for frequency on AC voltage 
        measurements, which can take values 100E-3, 1, 10, 100, 750, 
        as well as MIN, MAX, and DEF (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 750, "MAX", "MIN", "DEF"]
    )
    frequency_voltage_auto_range = Instrument.control(
        ":SENS:FREQ:VOLT:RANG:AUTO?", ":SENS:FREQ:VOLT:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC voltage in frequency measurements. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )
    frequency_aperture = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %s",
        """ A property that controls the frequency aperture in seconds,
        which sets the integration period and measurement speed. Takes values
        100 ms, 1 s, as well as MIN, MAX, and DEF (1 s). """,
        validator=strict_discrete_set,
        values=[100E-3, 1, "MIN", "MAX", "DEF"]
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(":READ?",
                                         """ Reads a temperature measurement in Celsius, based on the
                                         active :attr:`~.Agilent34450A.mode`. """
                                         )

    #############
    # Diode (V) #
    #############

    diode = Instrument.measurement(":READ?",
                                   """ Reads a diode measurement in Volts, based on the 
                                   active :attr:`~.Agilent34450A.mode`. """
                                   )

    ###################
    # Capacitance (F) #
    ###################

    capacitance = Instrument.measurement(":READ?",
                                         """ Reads a capacitance measurement in Farads, 
                                         based on the active :attr:`~.Agilent34450A.mode`. """
                                         )
    capacitance_range = Instrument.control(
        ":SENS:CAP:RANG?", ":SENS:CAP:RANG:AUTO 0;:SENS:CAP:RANG %s",
        """ A property that controls the capacitance range
        in Farads, which can take values 1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 
        1E-3, 10E-3, as well as MIN, MAX, and DEF (1E-6).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3, "MAX", "MIN", "DEF"]
    )
    capacitance_auto_range = Instrument.control(
        ":SENS:CAP:RANG:AUTO?", ":SENS:CAP:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for capacitance. """,
        validator=strict_discrete_set,
        values=[False, True],
        map_values=True
    )

    ####################
    # Continuity (Ohm) #
    ####################

    continuity = Instrument.measurement(":READ?",
                                        """ Reads a continuity measurement in Ohms, 
                                        based on the active :attr:`~.Agilent34450A.mode`. """
                                        )

    def __init__(self, adapter, **kwargs):
        super(Agilent34450A, self).__init__(
            adapter, "HP/Agilent/Keysight 34450A Multimeter", **kwargs
        )

        # Necessary to prevent VI_ERROR_TMO - Timeout expired before operation completed
        # Configuration changes can necessitate up to 8.8 secs (per datasheet)
        self.adapter.connection.timeout = 10000

        self.check_errors()

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 34450A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
            else:
                break

    def configure_voltage(self, range="AUTO", ac=False, resolution="DEF"):
        """ Configures the instrument to measure voltage.

        :param range: A voltage in Volts to set the voltage range or "AUTO"
        :param ac: False for DC voltage, True for AC voltage
        :param resolution: Desired resolution
        """
        if ac is True:
            self.mode = 'VOLT:AC'
            self.voltage_ac_resolution = resolution
            if range == "AUTO":
                self.voltage_ac_auto_range = True
            else:
                self.voltage_ac_range = range
        elif ac is False:
            self.mode = 'VOLT'
            self.voltage_resolution = resolution
            if range == "AUTO":
                self.voltage_auto_range = True
            else:
                self.voltage_range = range
        else:
            raise TypeError('Value of ac should be a boolean.')

    def configure_current(self, range="AUTO", ac=False, resolution="DEF"):
        """ Configures the instrument to measure current.

        :param range: A current in Amps to set the current range, or "AUTO"
        :param ac: False for DC current, and True for AC current
        :param resolution: Desired resolution
        """
        if ac is True:
            self.mode = 'CURR:AC'
            self.current_ac_resolution = resolution
            if range == "AUTO":
                self.voltage_ac_auto_range = True
            else:
                self.voltage_ac_range = range
        elif ac is False:
            self.mode = 'CURR:DC'
            self.current_resolution = resolution
            if range == "AUTO":
                self.voltage_auto_range = True
            else:
                self.voltage_range = range
        else:
            raise TypeError('Value of ac should be a boolean.')

    def configure_resistance(self, range="AUTO", wires=2, resolution="DEF"):
        """ Configures the instrument to measure resistance.

        :param range: A resistance in Ohms to set the resistance range, or"AUTO"
        :param wires: Number of wires used for measurement
        :param resolution: Desired resolution
        """
        if wires == 2:
            self.mode = 'RES'
            self.resistance_resolution = resolution
            if range == "AUTO":
                self.resistance_auto_range = True
            else:
                self.resistance_range = range
        elif wires == 4:
            self.mode = 'FRES'
            self.resistance_4W_resolution = resolution
            if range == "AUTO":
                self.resistance_4W_auto_range = True
            else:
                self.resistance_4W_range = range
        else:
            raise ValueError("Incorrect wires value, Agilent 34450A only supports 2 or 4 wire"
                             "resistance meaurement.")

    def configure_frequency(self, measured_from="voltage_ac",
                            measured_from_range="AUTO", aperture="DEF"):
        """ Configures the instrument to measure frequency.

        :param measured_from: "voltage_ac" or "current_ac"
        :param measured_from_range: range of measured_from signal.
        :param aperture: Aperture time in Seconds
        """
        if measured_from == "voltage_ac":
            self.mode = "VOLT:AC"
            if measured_from_range == "AUTO":
                self.frequency_voltage_auto_range = True
            else:
                self.frequency_voltage_range = measured_from_range
        elif measured_from == "current_ac":
            self.mode = "CURR:AC"
            if measured_from_range == "AUTO":
                self.frequency_current_auto_range = True
            else:
                self.frequency_current_range = measured_from_range
        else:
            raise ValueError('Incorrect value for measured_from parameter. Use '
                             '"voltage_ac" or "current_ac".')
        self.mode = 'FREQ'
        self.frequency_aperture = aperture

    def configure_temperature(self):
        """ Configures the instrument to measure temperature.
        """
        self.mode = 'TEMP'

    def configure_diode(self):
        """ Configures the instrument to measure diode voltage.
        """
        self.mode = 'DIOD'

    def configure_capacitance(self, range="AUTO"):
        """ Configures the instrument to measure capacitance.

        :param range: A capacitance in Farads to set the capacitance range, or "AUTO"
        """
        self.mode = 'CAP'
        if range == "AUTO":
            self.capacitance_auto_range = True
        else:
            self.capacitance_range = range

    def configure_continuity(self):
        """ Configures the instrument to measure continuity.
        """
        self.mode = 'CONT'

    def beep(self):
        """ Sounds a system beep.
        """
        self.write(":SYST:BEEP")




