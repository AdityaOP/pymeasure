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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import zmq
from msgpack_numpy import dumps
from traceback import format_exc
from time import sleep

from pymeasure.process import StoppableProcess
from .listeners import Recorder
from .results import Results
from .procedure import Procedure


class Worker(StoppableProcess):
    """ Worker runs the procedure and emits information about
    the procedure and its status over a ZMQ TCP port. In a child
    thread, a Recorder is run to write the results to 
    """

    def __init__(self, results, port):
        """ Constructs a Worker to perform the Procedure 
        defined in the file at the filepath
        """
        super(Worker, self).__init__()
        self.port = port
        if not isinstance(results, Results):
            raise ValueError("Invalid Results object during Worker construction")
        self.results = results
        self.procedure = self.results.procedure
        self.procedure.check_parameters()
        self.procedure.status = Procedure.QUEUED

    def join(self, timeout=0):
        try:
            super(Worker, self).join(timeout)
        except (KeyboardInterrupt, SystemExit):
            log.warning("User stopped Worker join prematurely")
            self.stop()
            super(Worker, self).join()

    def emit(self, topic, data):
        """ Emits data of some topic over TCP """
        if isinstance(topic, str):
            topic = topic.encode()
        log.debug("Emitting message: %s %s" % (topic, data))
        self.publisher.send_multipart([topic, dumps(data)])

    def update_status(self, status):
        self.procedure.status = status
        self.emit('status', status)

    def handle_exception(self, exception):
        log.error("Worker caught error in %r" % self.procedure)
        log.exception(exception)
        traceback_str = format_exc()
        self.emit('error', traceback_str)

    def run(self):
        self.recorder = Recorder(self.results, self.port)
        self.recorder.start()

        # route Procedure output
        self.procedure.should_stop = self.should_stop
        self.procedure.emit = self.emit

        self.context = zmq.Context.instance()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind('tcp://*:%d' % self.port)
        log.info("Worker connected to tcp://*:%d" % self.port)
        sleep(0.01)

        log.info("Running %r with %r" % (self.procedure, self))
        self.update_status(Procedure.RUNNING)
        self.emit('progress', 0.)
        self.procedure.startup()
        try:
            self.procedure.execute()
        except (KeyboardInterrupt, SystemExit):
            log.warning("User stopped Worker execution prematurely")
            self.update_status(Procedure.FAILED)
        except Exception as e:
            self.handle_exception(e)
            self.update_status(Procedure.FAILED)
        finally:
            self.procedure.shutdown()
            if self.procedure.status == Procedure.RUNNING:
                self.update_status(Procedure.FINISHED)
                self.emit('progress', 100.)
            self.recorder.stop()
            self.stop()

    def __repr__(self):
        return "<%s(port=%s,procedure=%s,should_stop=%s)>" % (
            self.__class__.__name__, self.port, 
            self.procedure.__class__.__name__, 
            self.should_stop()
        )