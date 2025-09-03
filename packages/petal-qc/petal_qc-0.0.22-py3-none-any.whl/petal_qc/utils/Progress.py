#!/usr/bin/env python3
"""An object usefull to show the progress of a process."""
import sys
import time


class GTimer(object):
    """A timer."""

    def __init__(self, do_start=False):
        """Initialization.

        Args:
        ----
            do_start: If True, start the timer. Defaults to False.

        """
        self._start = time.time()
        self._running = True
        self._end = self._start
        self._mark = self._start
        if do_start:
            self.start()

    def mark(self):
        """Time since last mark."""
        return time.time() - self._mark

    def set_mark(self):
        """Sets a time mark."""
        self._mark = time.time()

    def start(self):
        """Start the timer."""
        self._running = True
        self._start = time.time()

    def stop(self):
        """Stop the timer."""
        self._end = time.time()
        self._running = False
        return self._end - self._start

    def reset(self):
        """Reset the timer."""
        self._start = time.time()

    def __call__(self):
        """Get elapsed time since start."""
        if self._running:
            return time.time() - self._start
        else:
            return self._end - self._start


def rate_units(r):
    """Return the rate as a string with proper unitns."""
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
    """Return time as string with proper units."""
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
    """Shows the program status based on a counter."""

    def __init__(self, max_val, width=40):
        """Initialization.

        Args:
        ----
            max_val: Max value
            width (optional): The width of the message string.

        """
        self.width = width-2
        self.timer = GTimer()
        self.counter = 0.0
        self.max_val = float(max_val)
        self.prg = 0.0

    def start(self):
        """Start the process monitor."""
        self.counter = 0
        self.timer.start()

    def stop(self):
        """Stop th eprocess monitor."""
        self.timer.stop()

    def increase(self, val=1.0, show=False, interval=0.1):
        """Increase the counter and show message if requested.

        Args:
        ----
            val: Value of increment.
            show: True to show the message. Defaults to False.
            interval: Inerval to update message.

        """
        self.counter += val
        self.prg = self.counter/self.max_val
        if show:
            if self.timer.mark() > interval:
                self.timer.set_mark()
                self.show()

    def show(self):
        """Shows message."""
        self.show_stat(self.prg)

    def show_stat(self, x):
        """Show status of input value."""
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
        ss = '\rElapsed %4.1f %s %5.1f %s [%s>%s] %5.1f%% ERT %5.1f %s' % (te, teu, rv, ru, c21, c22, 100.*x, tr, tru)
        print(ss, end='')
        sys.stdout.flush()
