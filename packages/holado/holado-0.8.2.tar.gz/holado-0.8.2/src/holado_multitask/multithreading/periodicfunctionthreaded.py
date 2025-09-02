
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

from builtins import super
import logging
import threading
import time
from holado_multitask.multithreading.thread import InterruptableThread
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_core.common.tools.tools import Tools
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado.common.handlers.undefined import default_context

logger = logging.getLogger(__name__)


class PeriodicFunctionThreaded(InterruptableThread):
    '''
    Execute periodically in a thread given function with given arguments.
    
    Implementation uses a precise timer, in order to globally satisfy the desired periodicity (with a precision of around a nanosecond, depending to system latency).
    But implementation is quite simple, function is executed around each timer ticks : it is based on waits after function execution of the time needed to satisfy periodicity.
    If function execution is greater than periodicity, a warning is logged, and function is run immediately without waiting next timer tick.
    
    For fast periodicity, it is recommended to disable logs by setting property 'do_log' to False (and also 'do_log_warning' if needed).
    '''
    
    def __init__(self, period_seconds, target, args=None, kwargs=None, name=None, default_wait_timeout=None, register_thread=True, register_scope=default_context, delay_before_run_sec=None, nb_times=None):
        super().__init__(name if name is not None else f"PeriodicFunctionThreaded({repr(target)})", default_wait_timeout=default_wait_timeout, register_thread=register_thread, register_scope=register_scope, delay_before_run_sec=delay_before_run_sec)

        self.__period_seconds = period_seconds
        if self.__period_seconds < 1e-8:
            raise TechnicalException(f"Periodicity must be at least 10ns")
        self.__nb_times = nb_times
        self.__function_threaded = FunctionThreaded(target, args, kwargs)
        self.__do_log = True
        self.__do_log_warning = True
        
        if isinstance(self.__period_seconds, int) or self.__period_seconds % 1 < 1e-9 or self.__period_seconds % 1 > 1 - 1e-9:
            self.__timer = Tools.timer_s
            self.__timer_period = self.__period_seconds
            self.__timer_unity = "s"
            self.__timer_s_value = 1
        else:
            self.__timer = Tools.timer_ns
            self.__timer_period = self.__period_seconds * 1e9
            self.__timer_unity = "ns"
            self.__timer_s_value = 1e9

    @property
    def function_threaded(self):
        return self.__function_threaded

    @property
    def do_log(self):
        return self.__do_log

    @do_log.setter
    def do_log(self, do_log):
        self.__do_log = do_log

    @property
    def do_log_warning(self):
        return self.__do_log_warning

    @do_log_warning.setter
    def do_log_warning(self, do_log):
        self.__do_log_warning = do_log

    def run(self):
        logger.info(f"[{self.name}] Thread managing periodic function.")
        
        self.wait_before_run()
        
        start = self.__timer()
        count = 0
        while not self.is_interrupted:
            # Process function
            if self.do_log:
                logger.info(f"[{self.name}] Processing periodic iteration {count+1}...")
            beg = self.__timer()
            try:
                self.__function_threaded.run()
            except Exception as exc:
                msg = "[{}] Exception catched while processing function:\n    [{}]".format(self.name, repr(exc))
                logger.exception(msg)
            finally:
                count += 1
                iter_dur = self.__timer() - beg
                
            # Define next iteration timer
            next_timer = start + count * self.__timer_period
            wait_duration = next_timer - self.__timer()
            skip_wait = wait_duration < 0
            if skip_wait:
                if self.do_log_warning:
                    logger.warning(f"[{self.name}] {count}'th iteration finished too late (of {-wait_duration} {self.__timer_unity}) to process next iteration on time (duration: {iter_dur} {self.__timer_unity} ; periodicity: {self.__timer_period} {self.__timer_unity}). Processing immediatelly next iteration")
                
                while wait_duration + self.__timer_period < 0:
                    if self.do_log_warning:
                        logger.warning(f"[{self.name}] Failed to process {count+1}'th iteration, its activity period is passed")
                    count += 1
                    next_timer = start + count * self.__timer_period
                    wait_duration = next_timer - self.__timer()
            
            # Stop if nb_times is reached
            if self.__nb_times is not None:
                if count >= self.__nb_times:
                    break
            
            # Wait periodicity
            if not skip_wait:
                if self.do_log:
                    logger.info(f"[{self.name}] Waiting {wait_duration} {self.__timer_unity} to process next periodic function...")
                while not self.is_interrupted and threading.active_count() > 0:
                    if wait_duration > 0.1 * self.__timer_s_value:
                        time.sleep(0.1)
                        wait_duration = next_timer - self.__timer()
                    else:
                        if wait_duration > 1e-9 * self.__timer_s_value:
                            time.sleep(wait_duration / self.__timer_s_value)
                        break
                    
        logger.info(f"[{self.name}] Thead of periodic function has finished.")
        
        
