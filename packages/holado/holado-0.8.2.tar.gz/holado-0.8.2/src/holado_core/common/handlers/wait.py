
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of self software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and self permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
from holado_core.common.handlers.redo import Redo
from holado.common.handlers.undefined import undefined_value
from holado.holado_config import Config

logger = logging.getLogger(__name__)


class WaitOnEventResult(Redo):
    def __init__(self, name, on_event_func):
        super().__init__(name)
        self.__on_event_func = on_event_func
        self.__on_event_func_result = None
        
    def _process(self):
        return self.__on_event_func_result
    
    def on_event(self, *args, **kwargs):
        self.__on_event_func_result = self.__on_event_func(*args, **kwargs)


class WaitIsTrueOnEvent(WaitOnEventResult):
    def __init__(self, name, on_event_func):
        super().__init__(name, on_event_func)
        self.redo_until(True)


class WaitFuncResult(Redo):
    def __init__(self, name, func):
        super().__init__(name)
        self.__func = func
        
    def _process(self):
        return self.__func()

class WaitFuncResultVerifying(WaitFuncResult):
    def __init__(self, name, result_func, result_verify_func):
        super().__init__(name, result_func)
        self.__result_verify_func = result_verify_func
        
    def _is_redo_needed(self, result):
        return not self.__result_verify_func(result)


class WaitChange(WaitFuncResult):
    def __init__(self, name, func, *, do_process_in_thread=True, result_reference=undefined_value, timeout_seconds=None, polling_seconds=None):
        super().__init__(name, func)
        self.with_process_in_thread(do_process_in_thread)
        self.__result_reference = result_reference
        
        # Compute default timeout and polling if needed
        if timeout_seconds is None:
            timeout_seconds = Config.timeout_seconds
        if polling_seconds is None:
            polling_seconds = timeout_seconds / 1000
            if polling_seconds > 0.01:
                polling_seconds = 0.01
                
        self.with_timeout(timeout_seconds)
        self.polling_every(polling_seconds)
        
    def _is_redo_needed(self, result):
        if self.__result_reference is undefined_value:
            # Update reference with first run result
            self.__result_reference = result
            return True
        else:
            return result == self.__result_reference

class WaitEndChange(WaitFuncResult):
    def __init__(self, name, func, *, do_process_in_thread=True, result_reference=undefined_value, first_timeout_seconds=None, window_seconds=None, polling_seconds=None):
        super().__init__(name, func)
        self.with_process_in_thread(do_process_in_thread)
        self.__result_reference = result_reference
        
        # Compute default timeouts and duration if needed
        if window_seconds is None:
            if first_timeout_seconds is not None and first_timeout_seconds > 0:
                window_seconds = first_timeout_seconds / 10
            else:
                window_seconds = 1
            if window_seconds < 0.01:
                window_seconds = 0.01       # a window period below 10 ms is usually not efficient in testing context
        if polling_seconds is None:
            min_window = min(first_timeout_seconds, window_seconds) if first_timeout_seconds is not None else window_seconds
            polling_seconds = min_window / 100       # 1% of error on window detection
            if polling_seconds > 0.1:
                polling_seconds = 0.1       # a polling period over 100 ms is usually not efficient in testing context
            elif polling_seconds < 0.001:
                polling_seconds = 0.001       # a polling period below 1 ms is usually not efficient in testing context
        if first_timeout_seconds is None:
            first_timeout_seconds = window_seconds
        
        # Start with a timeout equal to first_timeout_seconds
        self.with_timeout(first_timeout_seconds)
        
        self.polling_every(polling_seconds)
        self.__window_seconds = window_seconds
    
    def _execute_after_process(self, result):
        if self.__result_reference is undefined_value:
            # Update reference with first run result
            self.__result_reference = result
        elif result != self.__result_reference:
            self.__result_reference = result
            
            # As a change is received, update timeout with window duration and do not raise on timeout anymore
            self.update_timeout(self.__window_seconds)
            self.without_raise_on_timeout()
        
    def _is_redo_needed(self, result):
        return True


