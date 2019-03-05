#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Agilent33220A(Instrument):
    """Represents the Agilent 33220A Arbitrary Waveform Generator.

    .. code-block:: python

        wfg = Agilent33220A("GPIB::10") # Default channel for the ITC503

        wfg.function = "SINUSOID"       # Sets a sine waveform
        wfg.frequency = 4.7e3           # Sets the frequency to 4.7 kHz
        wfg.voltage = 1                 # Set amplitude of 1 V

        wfg.burst = TRUE                # Enable burst mode
        wfg.burst_ncycles = 10          # A burst will consist of 10 cycles
        wfg.burst_mode = "TRIGGERED"    # A burst will be applied on a trigger
        wfg.trigger_source = "BUS"      # A burst will be triggered on TRG*

        wfg.output = TRUE               # Enable output of waveform generator
        wfg.trigger()                   # Trigger a burst

    """
    function = Instrument.control(
        "FUNC?", "FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, RAMP, PULS<E>, NOIS<E>, DC, USER. """,
        validator=strict_discrete_set,
        values=["SINUSOID", "SIN", "SQUARE", "SQU", "RAMP",
                "PULSE", "PULS", "NOISE", "NOIS", "DC", "USER"],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %s",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1e-6 (1 uHz) to 20e+6 (20 MHz), depending on the
        specified function. Can be set. """,
        validator=strict_range,
        values=[1e-6, 5e+6],
    )

    voltage = Instrument.control(
        "VOLT?", "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 1e-3 V to 10 V. Can be set. """,
        validator=strict_range,
        values=[10e-3, 10],
    )

    voltage_offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (10 - voltage) / 2). Can be set.
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.990 V to 5 V (must be higher than low
        voltage). Can be set. """,
        validator=strict_range,
        values=[-4.99, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.990 V (must be lower than high
        voltage). Can be set. """,
        validator=strict_range,
        values=[-5, 4.99],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYCL?", "FUNC:SQU:DCYCL %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %f",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 200 ns to 2000 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[2e-9, 2e3],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?", "FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYCL<E>. """,
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYCL", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?", "FUNC:PULS:WIDT %f",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 20 ns to 2000 s, within a
        set of restrictions depending on the period. Can be set. """,
        validator=strict_range,
        values=[2e-9, 2e3],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYCL?", "FUNC:PULS:DCYCL %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?", "FUNC:PULS:TRAN %f",
        """ A floating point property that controls the the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between 0.1 and 0.9 of the threshold. Valid values are between
        5 ns to 100 ns. Can be set. """,
        validator=strict_range,
        values=[5e-9, 100e-9],
    )

# OUTPut {OFF / ON} / ? {0:OFF, 1:ON}
    output = Instrument.control(
        "OUTP?", "OUTP %s",
        """ A property that turns on or off the output of the function
        generator. """)

# BURSt:STATe {OFF / ON} / ? {0:OFF, 1:ON}
    burst = Instrument.control(
        "BURSt:STAT?", "BURST:STAT %s",
        """
        """,
    )

    burst_mode = Instrument.control(
        "BURS:MODE?", "BURS:MODE %s",
        """ A string property that controls the burst mode. Valid values
        are: TRIG<GERED>, GAT<ED>. This setting can be set. """,
        validator=strict_discrete_set,
        values=["TRIG", "TRIGGERED", "GAT", "GATED"],
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYCL?", "BURS:NCYCL %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 50000. This can be
        set. """,
        validator=strict_discrete_set,
        values=range(1, 50001),
    )

    def trigger(self):
        """ Send a trigger signal to the function generator. """
        self.write("TRG*;WAI*")

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """ A string property that controls the trigger source. Valid values
        are: IMM<EDIATE> (internal), EXT<ERNAL> (rear input), BUS (via trigger
        command). This setting can be set. """,
        validator=strict_discrete_set,
        values=["IMM", "IMMEDIATE", "EXT", "EXTERNAL", "BUS"],
    )

# OUTput:TRIGger {OFF / ON} / ? {0:OFF, 1:ON}

    remote_local_state = Instrument.setting(
        "SYST:COMM:RLST %s",
        """ A string property that controls the remote/local state of the
        function generator. Valid values are: LOC<AL>, REM<OTE>, RWL<OCK>.
        This setting can only be set. """,
        validator=strict_discrete_set,
        values=["LOC", "LOCAL", "REM", "REMOTE", "RWL", "RWLOCK"],
    )

    def check_errors(self):
        """ Read all errors from the instrument. """
        while True:
            err = self.values("SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 33220A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
            else:
                break
