
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from holado_multitask.multithreading.thread import InterruptableThread
from threading import Event
from holado.common.handlers.undefined import default_context


class Timer(InterruptableThread):
    """ Helper class managing a timer.
    
    The functional code is a copy of threading.Timer, but it inherists from HolAdo Thread class.
    """
    
    def __init__(self, name, interval, function, args=None, kwargs=None, default_wait_timeout=None, register_thread=True, register_scope=default_context, delay_before_run_sec=None):
        super().__init__(name, default_wait_timeout=default_wait_timeout, register_thread=register_thread, register_scope=register_scope, delay_before_run_sec=delay_before_run_sec)
        
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def interrupt(self):
        self.cancel()
        super().interrupt()
        
    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        # Wait timer interval or canceled (ie finished==True)
        self.finished.wait(self.interval)
        
        # Run function if not canceled
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()


