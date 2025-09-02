#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time, sleep
from threading import Thread, Lock
import numpy as np
from functools import wraps
from io import StringIO
import logging
from colorama import just_fix_windows_console, Fore, Style

just_fix_windows_console()

TICTOC = 19

logging.addLevelName(TICTOC, 'TICTOC')
logging.TICTOC = TICTOC
logging.getLoggerClass().tictoc = lambda self, message, *args, **kwargs:\
    self._log(TICTOC, message, args, **kwargs) if self.isEnabledFor(TICTOC) else None
logging.tictoc = lambda message, *args, **kwargs:\
    logging.log(TICTOC, message, *args, **kwargs)

class Delay(Thread):

    def __init__(self, timeout, passed_callback=lambda: None):
        Thread.__init__(self)
        self.lock = Lock()
        self.timeout = timeout
        self.passed = False
        self.stopped = False
        self.passed_callback = passed_callback
        self.start()

    def stop(self):
        if self.lock.locked():
            self.stopped = True
            self.lock.release()

    def run(self):
        self.lock.acquire()
        self.lock.acquire(timeout=self.timeout)
        try:
            self.lock.release()
        except:
            pass
        if not self.stopped:
            self.passed = True
            self.passed_callback()

    @property
    def status(self):
        if self.lock.locked():
            return "still running"
        if self.passed:
            return "passed"
        if self.stopped:
            return "stopped"


class Tictoc:

    journal = {}
    global_timeout = 0.5
    running = []

    def __init__(self, name=None, speak=True, timeout=None):
        self.speak = speak
        self._timeout = timeout
        self.name = name
        self.delay = None
        if self.name is not None:
            if self.name not in self.journal:
                self.journal[self.name] = []

    def print_start(self):
        if self.name is not None:
            logging.tictoc(f"{Fore.RED}{self.name}{Style.RESET_ALL} started")

    def print_end(self, duration):
        if self.name is not None:
            logging.tictoc(f"{Fore.GREEN}{self.name}{Style.RESET_ALL} finished in {duration:0.6f} s.")

    def __enter__(self):
        self.tstart = time()
        self.running.append(self)
        if self.speak and self.timeout > 0:
            self.delay = Delay(self.timeout, passed_callback=self.print_start)
        elif self.speak:
            self.print_start()
        return self

    @property
    def timeout(self):
        if self._timeout is not None:
            return self._timeout
        return self.global_timeout

    def __exit__(self, type, value, traceback):
        duration = time() - self.tstart
        if self.speak and self.timeout > 0:
            self.delay.stop()
            if self.delay.status == "stopped":
                self.speak = False
        if self.name is not None:
            self.journal[self.name].append(duration)
        if self.speak:
            self.print_end(duration)
        self.running.remove(self)


def tictoc(func=None, speak=True, timeout=None):
    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Tictoc(func.__name__, speak, timeout=timeout):
                response = func(*args, **kwargs)
            return response
        return wrapper
    if func is None:
        def decorator(func):
            return decorated(func)
        return decorator
    return decorated(func)

def summary():
    import pandas as pd
    s = max([len(k) for k in Tictoc.journal])
    results = []
    for k, v in Tictoc.journal.items():
        d = np.array(v)
        results.append([k.ljust(s), d.min(), d.max(), d.mean(), d.sum(), d.size])
    results.sort()
    txt = "func,min,max,mean,sum,ncall"
    for r in results:
        txt += "\n%s,%2.6f,%2.6f,%2.6f,%2.6f,%d" % tuple(r)
    txt = pd.read_csv(StringIO(txt)).to_string(index=False)
    print('='*len(txt.split('\n')[0]))
    print(txt)
    print('='*len(txt.split('\n')[0]))









