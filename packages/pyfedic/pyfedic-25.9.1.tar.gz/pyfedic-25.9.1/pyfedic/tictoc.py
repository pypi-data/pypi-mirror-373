#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time, sleep
from threading import Thread, Lock
import numpy as np
from functools import wraps
from io import StringIO
import logging
from rich.console import Console
from rich.table import Table

console = Console()

TICTOC = 19

logging.addLevelName(TICTOC, 'TICTOC')
logging.TICTOC = TICTOC

def _tictoc(message, *args, **kwargs):
    for h in logging.getLogger().handlers:
        if not hasattr(h, '_tictoc_setup'):
            h._tictoc_setup = 1
            if isinstance(h, logging.StreamHandler) and h.stream.name == '<stderr>':
                old_emit = h.emit
                def new_emit(record):
                    if record.levelno == TICTOC:
                        console.print(console.render_str('TICTOC :: ') + record.msg)
                    else:
                        return old_emit(record)
                h.emit = new_emit
    logging.log(TICTOC, console.render_str(message), *args, **kwargs)

logging.tictoc = _tictoc


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
            logging.tictoc(f"[red]{self.name}[/red] started")

    def print_end(self, duration):
        if self.name is not None:
            logging.tictoc(f"[green]{self.name}[/green] finished in {duration:0.6f} s.")

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
    s = max([len(k) for k in Tictoc.journal])
    results = []
    for k, v in Tictoc.journal.items():
        d = np.array(v)
        results.append([k.ljust(s), d.min(), d.max(), d.mean(), d.sum(), d.size])
    results.sort()

    table = Table()

    table.add_column("func", justify="left", no_wrap=True)
    table.add_column("min", justify="right")
    table.add_column("max", justify="right")
    table.add_column("mean", justify="right")
    table.add_column("sum", justify="right")
    table.add_column("ncall", justify="right")

    for r in results:
        table.add_row(*[f"{x:0.3f}" if isinstance(x, float) else str(x) for x in r])

    console.print(table)







