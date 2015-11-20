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

from .qt_variant import QtCore

import zmq
from msgpack import loads
from time import sleep
from multiprocessing import Event

from .thread import StoppableQThread
from ..experiment.procedure import Procedure


class QListener(StoppableQThread):
    """Base class for QThreads that need to listen for messages
    on a ZMQ channel and can be stopped by a thread- and process-safe
    method call
    """

    def __init__(self, channel, topic=''):
        """ Constructs the Listener object with a subscriber channel 
        over which to listen for messages

        :param channel: Channel to listen on
        """
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(channel)
        self.subscriber.setsocketopt(zmq.SUBSCRIBE, topic.encode())
        super(QListener, self).__init__()

    def receive(self):
        topic, raw_data = self.subscriber.recv()
        return topic, loads(raw_data)

    def __repr__(self):
        return "<%s(channel=%s,topic=%s,should_stop=%s)>" % (
            self.__class__.__name__, channel, topic, self.should_stop())


class ProcedureMonitor(QListener):
    """ ProcedureMonitor listens for status and progress messages
    on a ZMQ channel and routes them to signals and slots
    """

    status = QtCore.QSignal(int)
    progress = QtCore.QSignal(float)
    running = QtCore.QSignal()
    failed = QtCore.QSignal()
    finished = QtCore.QSignal()

    def __init__(self, channel):
        super(ProcedureMonitor, self).__init__(channel, topic='')

    def run(self):
        while not self.should_stop():
            topic, data = self.receive()
            if topic == 'status':
                self.status.emit(data)
                if data == Procedure.FAILED:
                    self.failed.emit()
                elif data == Procedure.FINISHED:
                    self.finished.emit()
            elif topic == 'progress':
                self.progress.emit(data)
            sleep(0.01)





