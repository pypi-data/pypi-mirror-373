
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
from holado_multitask.multithreading.functionthreaded import FunctionThreaded
from holado_multitask.multithreading.loopthread import LoopThread
from holado.common.handlers.undefined import default_context

logger = logging.getLogger(__name__)


class LoopFunctionThreaded(LoopThread):
    '''
    Execute in a thread given function with given arguments.
    '''
    
    def __init__(self, target, args=None, kwargs=None, name=None, default_wait_timeout=None, register_thread=True, register_scope=default_context, delay_before_run_sec=None, nb_times=None):
        super().__init__(name if name is not None else f"Loop function '{target}'", default_wait_timeout=default_wait_timeout, register_thread=register_thread, register_scope=register_scope, delay_before_run_sec=delay_before_run_sec, nb_times=nb_times)

        self.__function_threaded = FunctionThreaded(target, args, kwargs)

    @property
    def function_threaded(self):
        return self.__function_threaded

    def run_loop(self):
        try:
            self.__function_threaded.run()
        except Exception as exc:
            msg = "Exception catched while processing function:\n    [{}]".format(repr(exc))
            logger.exception(msg)
    
    
    
