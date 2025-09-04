#!/usr/bin/env python
""" A Timer class
"""
import time


class GTimer(object):
    """ A timer
    """

    def __init__(self, do_start=False):
        self._start = time.time()
        self._running = True
        self._end = self._start
        self._mark = self._start
        if do_start:
            self.start()

    def mark(self):
        return time.time() - self._mark

    def set_mark(self):
        self._mark = time.time()

    def start(self):
        self._running = True
        self._start = time.time()

    def stop(self):
        self._end = time.time()
        self._running = False
        return self._end - self._start

    def reset(self):
        self._start = time.time()

    def __call__(self):
        if self._running:
            return time.time() - self._start
        else:
            return self._end - self._start


if __name__ == "__main__":
    T = GTimer()
    print("Measuring 0.5 seconds")
    T.start()
    time.sleep(0.5)
    print("%.2f" % T.stop())
