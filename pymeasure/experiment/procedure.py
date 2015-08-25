#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands
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

from .parameters import Parameter


class Procedure(object):
    """Provides the base class of a procedure to organize the experiment
    execution. Procedures should be run in ProcedureThreads to ensure that
    concurrent control is properly managed.

    .. code-block:: python

        procedure = Procedure()
        thread = ProcedureThread() # or QProcedureThread()
        thread.load(procedure)
        thread.start()

    Inhereting classes are required to define the enter, execute,
    and exit methods. The exit method is called on independent of the
    sucessful completion, software error, or abort of code run in the
    execute method.
    """

    DATA_COLUMNS = []
    FINISHED, FAILED, ABORTED, QUEUED, RUNNING = 0, 1, 2, 3, 4

    _parameters = {}

    def __init__(self):
        self.status = Procedure.QUEUED
        self._update_parameters()

    def _update_parameters(self):
        """ Collects all the Parameter objects for this procedure and stores
        them in a meta dictionary so that the actual values can be set in their
        stead
        """
        if not self._parameters:
            self._parameters = {}
        for item in dir(self):
            parameter = getattr(self, item)
            if isinstance(parameter, Parameter):
                self._parameters[item] = parameter
                if parameter.is_set():
                    setattr(self, item, parameter.value)
                else:
                    setattr(self, item, None)

    def parameters_are_set(self):
        """ Returns True if all parameters are set """
        for name, parameter in self._parameters.items():
            if getattr(self, name) is None:
                return False
        return True

    def check_parameters(self):
        """ Raises an exception if any parameter is missing before calling
        the associated function. Ensures that each value can be set and
        got, which should cast it into the right format. Used as a decorator
        @checkParameters on the enter method
        """
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is None:
                raise NameError("Missing %s '%s' in %s" % (
                    parameter.__class__, name, self.__class__))

    def parameter_values(self):
        """ Returns a dictionary of all the Parameter values and grabs any
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                setattr(self, name, parameter.value)
                result[name] = parameter.value
            else:
                result[name] = None
        return result

    def parameter_objects(self):
        """ Returns a dictionary of all the Parameter objects and grabs any
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                setattr(self, name, parameter.value)
            result[name] = parameter
        return result

    def refresh_parameters(self):
        """ Enforces that all the parameters are re-cast and updated in the meta
        dictionary
        """
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            parameter.value = value
            setattr(self, name, parameter.value)

    def set_parameters(self, parameters, except_missing=True):
        """ Sets a dictionary of parameters and raises an exception if additional
        parameters are present if except_missing is True
        """
        for name, value in parameters.items():
            if name in self._parameters:
                self._parameters[name].value = value
                setattr(self, name, self._parameters[name].value)
            else:
                if except_missing:
                    raise NameError("Parameter '%s' does not belong to '%s'" % (
                            name, repr(self)))

    def enter(self):
        """ Executes the commands needed at the start-up of the measurement
        """
        pass

    def execute(self):
        """ Preforms the commands needed for the measurement itself. During
        execution the exit method will always be run following this method.
        This includes when Exceptions are raised.
        """
        pass

    def exit(self):
        """ Executes the commands necessary to shut down the instruments
        and leave them in a safe state.
        """
        pass

    def __str__(self):
        result = repr(self) + "\n"
        for name, obj in self.parameterObjects().items():
            if obj.unit:
                result += "%s: %s %s\n" % (obj.name, obj.value, obj.unit)
            else:
                result += "%s: %s\n" % (obj.name, obj.value)
        return result


class UnknownProcedure(Procedure):
    """ Handles the case when a :class:`.Procedure` object can not be imported
    during loading in the :class:`.Results` class
    """

    def __init__(self, parameters):
        self._parameters = parameters

    def enter(self):
        raise Exception("UnknownProcedure can not be run")
