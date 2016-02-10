#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 Colin Jermain, Graham Rowlands, Guen Prawiroatmodjo
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
from .results import unique_filename
from .config import get_config, set_mpl_rcparams
from pymeasure.log import setup_logging, console_log
from pymeasure.experiment import Results, Worker
from .parameters import Measurable
from IPython import display
import time, signal
import numpy as np
import tempfile
import gc
import logging
log = logging.getLogger()
log.addHandler(logging.NullHandler())

def get_array(start, stop, step):
    '''Returns a numpy array from start to stop'''
    step = np.sign(stop-start)*abs(step)
    return np.arange(start, stop+step, step)

def get_array_steps(start, stop, numsteps):
    '''Returns a numpy array from start to stop in numsteps'''
    return get_array(start, stop, (abs(stop-start)/numsteps))

def get_array_zero(maxval, step):
    '''Returns a numpy array from 0 to maxval to -maxval to 0'''
    return np.concatenate((np.arange(0,maxval,step), np.arange(maxval, -maxval, -step), np.arange(-maxval, 0, step)))

def create_filename(title):
    config = get_config()
    if 'Filename' in config._sections.keys():
        filename = unique_filename(suffix='_%s' %title, **config._sections['Filename'])
    else:
        filename = tempfile.mktemp()
    return filename

class Experiment():
    '''Class for running procedures.'''
    def __init__(self, title, procedure, analyse=(lambda x: x)):
        self.title = title
        self.procedure = procedure
        self.measlist = []
        self.port = 5888
        self.plots = []
        self.figs = []
        self._data = []
        self.analyse = analyse

        config = get_config()
        set_mpl_rcparams(config)
        if 'Logging' in config._sections.keys():
            self.scribe = setup_logging(log, **config._sections['Logging'])
        else:
            self.scribe = console_log(log)
        self.scribe.start()

        self.filename = create_filename(self.title)
        log.info("Using data file: %s" % self.filename)

        self.results = Results(self.procedure, self.filename)
        log.info("Set up Results")

        self.worker = Worker(self.results, self.scribe.queue, logging.DEBUG)
        log.info("Create worker")

    def start(self):
        log.info("Starting worker...")
        self.worker.start()

    @property
    def data(self):
        self._data = self.analyse(self.results.data.copy())
        return self._data

    def plot_live(self, *args, **kwargs):
        t=time.time()
        while self.data.empty:
            time.sleep(.1)
            if (time.time()-t)>10:
                log.warning('Timeout, no data received for liveplot')
        self.plot(*args, **kwargs)
        while not self.worker.should_stop():
            self.plot(*args, **kwargs)
        display.clear_output(wait=True)
        if self.worker.is_alive():
            self.worker.terminate()

    def plot(self, *args, **kwargs):
        if not self.plots:
            kwargs['title'] = self.title
            ax = self.data.plot(*args, **kwargs)
            self.plots.append({'type': 'plot', 'args': args, 'kwargs': kwargs, 'ax': ax})
            if ax.get_figure() not in self.figs:
                self.figs.append(ax.get_figure())
            self._user_interrupt = False
        else:
            self.update_plot()

    def clear_plot(self):
        for fig in self.figs:
            fig.clf()
            pl.close()
        self.figs = []
        self.plots = []
        gc.collect()

    def update_plot(self):
        try:
            tasks = []
            self.data
            for plot in self.plots:
                ax = plot['ax']
                if plot['type']=='plot':
                    x,y = plot['args'][0], plot['args'][1]
                    if type(y) == str:
                        y = [y]
                    for yname,line in zip(y,ax.lines):
                        self.update_line(ax, line, x, yname)
                if plot['type']=='pcolor':
                    x,y,z = plot['x'], plot['y'], plot['z']
                    update_pcolor(ax, x, y, z)
            
            display.clear_output(wait=True)
            display.display(*self.figs)
            time.sleep(0.1)
        except KeyboardInterrupt:
            display.clear_output(wait=True)
            display.display(*self.figs)
            self._user_interrupt = True
    
    def pcolor(self, xname, yname, zname, *args, **kwargs):
        title = self.title
        x,y,z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0]*shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        ax = sns.heatmap(df)
        pl.title(title)
        pl.xlabel(xname)
        pl.ylabel(yname)
        ax.invert_yaxis()
        pl.plt.show()
        self.plots.append({'type': 'pcolor', 'x':xname, 'y':yname, 'z':zname, 'args':args, 'kwargs':kwargs, 'ax':ax})
        if ax.get_figure() not in self.figs:
            self.figs.append(ax.get_figure())
    
    def update_pcolor(self, ax, xname, yname, zname):
        x,y,z = self._data[xname], self._data[yname], self._data[zname]
        shape = (len(y.unique()), len(x.unique()))
        diff = shape[0]*shape[1] - len(z)
        Z = np.concatenate((z.values, np.zeros(diff))).reshape(shape)
        df = pd.DataFrame(Z, index=y.unique(), columns=x.unique())
        cbar_ax = ax.get_figure().axes[1]
        sns.heatmap(df, ax=ax, cbar_ax=cbar_ax)
        ax.set_xlabel(xname)
        ax.set_ylabel(yname)
        ax.invert_yaxis()

    def update_line(self, ax, hl, xname, yname):
        del hl._xorig, hl._yorig
        hl.set_xdata(self._data[xname])
        hl.set_ydata(self._data[yname])
        ax.relim()
        ax.autoscale()
        gc.collect()