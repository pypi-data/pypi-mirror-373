#!/usr/bin/env python3
""" An object usefull to show the progress of a process.
"""
import sys
try:
    from GTimer import GTimer
except ImportError:
    from vdaq_ana.GTimer import GTimer

def rate_units(r):
    units = "Hz"
    if r > 1.0e6:
        r /= 1.0e6
        units = "MHz"

    elif r > 1.0e3:
        r /= 1.0e3
        units = "kHz"

    elif r > 1.0:
        pass

    elif r > 1e-3:
        r /= 1.0e-3
        units = "mHz"

    else:
        r /= 1.0e-6
        units = "uHz"

    return r, units


def time_units(t):
    units = "s"
    if t > 86400.0:
        t /= 86400.0
        units = "d "

    elif t > 3600.0:
        t /= 3600.0
        units = "h "

    elif t > 60.0:
        t /= 60.0
        units = "m "

    elif t > 1.0:
        units = "s "

    elif t > 1.0e-3:
        t /= 1.0e-3
        units = "ms"

    elif t > 1.0e-6:
        t /= 1.0e-6
        units = "us"

    else:
        t /= 1.0e-9
        units = "ns"

    return t, units


class ShowProgress(object):
    """ This class shows the program status.
    """

    def __init__(self, max_val, width=40):
        self.width = width-2
        self.timer = GTimer()
        self.counter = 0.0
        self.max_val = float(max_val)
        self.prg = 0.0

    def start(self):
        self.counter = 0
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def increase(self, val=1.0, show=False, interval=0.1):
        self.counter += val
        self.prg = self.counter/self.max_val
        if show:
            if self.timer.mark() > interval:
                self.timer.set_mark()
                self.show()

    def show(self):
        self.show_stat(self.prg)

    def show_stat(self, x):
        n21 = int(x*self.width)
        n22 = int(self.width-n21-1)

        c21 = n21*'='
        c22 = n22*' '
        if self.prg > 0.0:
            tt = self.timer()*(1.0/self.prg-1.0)
        else:
            tt = 0.0

        rate = self.counter/self.timer()
        rv, ru = rate_units(rate)
        te, teu = time_units(self.timer())
        tr, tru = time_units(tt)

#        ss = '\r[%s>%s] %5.1f%% %8d' % (c21 , c22, 100.*x, self.counter)
        ss = '\rElapsed %4.1f %s %5.1f %s [%s>%s] %5.1f%% ERT %5.1f %s' % (te, teu, rv, ru, c21, c22, 100.*x,  tr, tru)
        print(ss, end='')
        sys.stdout.flush()
