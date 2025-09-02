
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

import logging
from holado_core.common.block.function import Function
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_multitask.multiprocessing.process import InterruptableProcess

logger = logging.getLogger(__name__)


class FunctionProcess(InterruptableProcess):
    '''
    Execute in a process given function with given arguments
    '''
    
    def __init__(self, target, args=None, kwargs=None, name = None, default_wait_timeout = None, register_process = True, delay_before_run_sec=None):
        super().__init__(name if name is not None else f"FunctionProcess({repr(target)})", default_wait_timeout = default_wait_timeout, register_process = register_process, delay_before_run_sec=delay_before_run_sec)
        
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        self._function = Function(target, *args, **kwargs)
        self.__error = None
        self.__result = None
        self.__interrupt_function = None
        self.__callback_function = None

    @property
    def error(self):
        return self.__error

    @property
    def result(self):
        return self.__result

    @property
    def interrupt_function(self):
        return self.__interrupt_function

    @interrupt_function.setter
    def interrupt_function(self, func):
        """Set the Function to call on interrupt"""
        self.__interrupt_function = func

    @property
    def callback_function(self):
        return self.__callback_function

    @callback_function.setter
    def callback_function(self, func):
        """Set the callback function"""
        self.__callback_function = func
 
    def run(self):
        # Start running by superclass run
        super().run()
        
        # self._raise_if_interrupted()
        self.wait_before_run()
            
        # self._raise_if_interrupted()
        try:
#             logging.debug("+++++++++ Launching function [{}({})]".format(repr(self._target), repr(self._args)))
            self.__result = self._function.run()
        except Exception as exc:
            logger.exception(f"[{self.name}] Exception catched during processed function [{self._function.represent()}]")
            self.__error = exc
        
        # self._raise_if_interrupted()
        try:
            if self.__callback_function:
                self.__callback_function.run(self.result, self.error)
        except Exception as exc:
            msg = f"[{self.name}] Exception catched while calling callback function:\n    callback_function: {repr(self.__callback_function)}\n    result: [{Tools.truncate_text(repr(self.result))}]\n    error: [{repr(self.error)}]"
            logger.exception(msg)
            raise FunctionalException(msg) from exc
        
        logger.info(f"[{self.name}] Process has finished")

    def throw_if_error(self):
        if self.error:
            raise FunctionalException(f"[{self.name}] Error during call of function [{repr(self._target)}({repr(self._args)})]") from self.error
    
    def interrupt(self):
        if not self.is_interrupted and self.is_alive():
            super().interrupt()
            if self.interrupt_function is not None:
                self.interrupt_function.run()
