import sys
import random
import tempfile
from time import sleep
import pyqtgraph as pg

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results
from pymeasure.display.qt_variant import QtGui
from pymeasure.display.manager import Experiment, ManagedWindow
from pymeasure.display.browser import BrowserItem
from pymeasure.display.graph import ResultsCurve

console_log(log, level=logging.INFO)


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', unit='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)

    def execute(self):
        log.info("Starting to generate numbers")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number': random.random()
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100*i/self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=TestProcedure,
            browser_columns=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )

    def queue(self):
        filename = tempfile.mktemp()

        procedure = TestProcedure()
        procedure.iterations = 200
        procedure.delay = 0.1

        results = Results(procedure, filename)

        color = pg.intColor(self.browser.topLevelItemCount() % 8)
        curve = ResultsCurve(results, x=self.x_axis, y=self.y_axis, 
            pen=pg.mkPen(color=color, width=2), antialias=False)
        curve.setSymbol(None)
        curve.setSymbolBrush(None)

        browser_item = BrowserItem(results, curve)
        experiment = Experiment(results, curve, browser_item)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())