
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

import threading
import time
import datetime
import logging
import holado_multitask.multithreading.thread as ctt
from holado.common.handlers.undefined import default_context

logger = logging.getLogger(__name__)


class LoopThread(ctt.InterruptableThread):
    """ Helper class managing a loop in a thread."""

    def __init__(self, name, default_wait_timeout = None, register_thread=True, register_scope=default_context, delay_before_run_sec=None, nb_times=None):
        super().__init__(name, default_wait_timeout=default_wait_timeout, register_thread=register_thread, register_scope=register_scope, delay_before_run_sec=delay_before_run_sec)
        
        self.__nb_times = nb_times
        
        # Manage loops
        self.__is_under_loop = threading.Event()
        self.__next_loop_datetime = datetime.datetime.now()
        self.__loop_counter = 0
        
    @property
    def next_loop_datetime(self):
        return self.__next_loop_datetime

    @next_loop_datetime.setter
    def next_loop_datetime(self, dt):
        self.__next_loop_datetime = dt

    @property
    def loop_counter(self):
        return self.__loop_counter
        
    def run(self):
        logger.info("Loop thread '{}' is launched.".format(self.name))
        
        counter = 0
        while not self.is_interrupted:
#             logger.debug("[Thread '{}'] New run".format(self.name))
            try:
                if self.does_need_run_loop():
                    with self._is_lock:
                        self._is_idle.clear()
                        self.__is_under_loop.set()
                        self.__loop_counter += 1
                    
                    self.run_loop()
                    counter += 1
                    
                    with self._is_lock:
                        self.__is_under_loop.clear()
                        self._is_idle.set()
                        
                    # Stop if nb_times is reached
                    if self.__nb_times is not None:
                        if counter >= self.__nb_times:
                            break
                else:
                    time.sleep(self._get_sleep_time_before_next_loop())
                    
            except:
                logger.exception("[Thread '{}'] Exception catched during loop".format(self.name))

        logger.info("Loop thread '{}' has finished.".format(self.name))
        
    def does_need_run_loop(self):
        return datetime.datetime.now() >= self.__next_loop_datetime
    
    def _get_sleep_time_before_next_loop(self):
        now = datetime.datetime.now()
        if now < self.__next_loop_datetime:
            delta = self.__next_loop_datetime - now
            res = delta.total_seconds()
            if res > 1:
                return 1
            else:
                return res
        return 0
    
    def run_loop(self):
        raise NotImplementedError()

    def wait_is_under_loop(self, timeout=None):
        self._wait(self.__is_under_loop, "is under loop", timeout=timeout)

