
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
from holado_core.common.block.function import Function
from holado_core.common.exceptions.functional_exception import FunctionalException
import holado_multitask.multithreading.thread as ctt
from holado_core.common.tools.tools import Tools
import time
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import default_context

logger = logging.getLogger(__name__)


class FunctionThreaded(ctt.InterruptableThread):
    '''
    Execute in a thread given function with given arguments
    '''
    
    def __init__(self, target, args=None, kwargs=None, name=None, default_wait_timeout=None, register_thread=True, register_scope=default_context, delay_before_run_sec=None, do_log=True):
        super().__init__(name if name is not None else f"FunctionThreaded({repr(target)})", default_wait_timeout=default_wait_timeout, register_thread=register_thread, register_scope=register_scope, delay_before_run_sec=delay_before_run_sec)
        
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        self._function = Function(target, *args, **kwargs)
        self.__error = None
        self.__result = None
        
        # Manage interrupt
        self.__interrupt_needs_function = True
        self.__interrupt_function = None
        
        self.__callback_function = None
        self.__do_log = do_log

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
    def interrupt_needs_function(self):
        return self.__interrupt_needs_function

    @interrupt_needs_function.setter
    def interrupt_needs_function(self, need_func):
        """Set if interrupt_function is needed by interrupt"""
        self.__interrupt_needs_function = need_func

    @property
    def callback_function(self):
        return self.__callback_function

    @callback_function.setter
    def callback_function(self, func):
        """Set the callback function"""
        self.__callback_function = func
 
    def run(self):
        if self.delay_before_run_seconds is not None:
            try:
                time.sleep(self.delay_before_run_seconds)
            except Exception as exc:
                if self.__do_log:
                    logger.exception(f"[Thread '{self.name}'] Exception while waiting delay before run (delay: {self.delay_before_run_seconds} ; type: {Typing.get_object_class_fullname(self.delay_before_run_seconds)})")
            
        if self.is_interrupted:
            return
        
        try:
#             logging.debug("+++++++++ Launching function [{}({})]".format(repr(self._target), repr(self._args)))
            self.__result = self._function.run()
        except Exception as exc:
            if self.__do_log:
                logger.exception(f"[Thread '{self.name}'] Exception catched during threaded function [{self._function.represent()}]")
            self.__error = exc
        
        if self.is_interrupted:
            return
        
        try:
            if self.__callback_function:
                self.__callback_function.run(self.result, self.error)
        except Exception as exc:
            msg = "Exception catched while calling callback function:\n    callback_function: {}\n    result: [{}]\n    error: [{}]".format(repr(self.__callback_function), Tools.truncate_text(repr(self.result)), repr(self.error))
            if self.__do_log:
                logger.exception(msg)
            raise FunctionalException(msg) from exc
        
        if self.__do_log:
            # logger.info(f"[Thread '{self.name}'] Thread has finished")
            logger.info(f"[Thread '{self.name}'] Thread has finished (func: {self._function})")

    def throw_if_error(self):
        if self.error:
            raise FunctionalException("Error during call of function [{}({})]".format(repr(self._target), repr(self._args))) from self.error
    
    @property
    def is_interruptable(self):
        return not self.__interrupt_needs_function or self.__interrupt_function is not None

    def interrupt(self):
        if not self.is_interrupted and self.is_alive():
            super().interrupt()
            if self.interrupt_function is not None:
                self.interrupt_function.run()


