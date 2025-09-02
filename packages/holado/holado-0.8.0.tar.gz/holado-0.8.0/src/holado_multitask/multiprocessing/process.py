
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

from holado.holado_config import Config
import logging
import multiprocessing
import time
from holado.common.context.session_context import SessionContext
from holado_multitask.multitasking.multitask_manager import MultitaskManager
from holado_python.standard_library.typing import Typing
from holado.common.handlers.undefined import undefined_argument
from holado_core.common.exceptions.technical_exception import TimeoutTechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException

logger = logging.getLogger(__name__)


class Process(multiprocessing.context.Process):
    """ Helper class managing a multiprocessing process.
    WARNING: Do not use, it is under construction
    """
    
    def __init__(self, name, default_wait_timeout = None, register_process = True, delay_before_run_sec=None):
        super().__init__()
        
        if default_wait_timeout is None:
            default_wait_timeout = Config.timeout_seconds * 1000
            
        self.__name = name
        self.__unique_name = SessionContext.instance().multitask_manager.prepare_process(name)
        self.__default_wait_timeout = default_wait_timeout
        self.__delay_before_run_sec = delay_before_run_sec

        # Put process as daemon
        self.daemon = True
        
        # Manage process status
        # self._is_lock = threading.Lock()
        # self._is_idle = threading.Event()
        # self._is_idle.set()
        
        # Register process
        if register_process:
            # Registered name has to be unique
            SessionContext.instance().processes_manager.register_process(self.__unique_name, self)
        
    @property
    def name(self):
        return self.__name
    
    @property
    def unique_name(self):
        return self.__unique_name
    
    @property
    def default_wait_timeout(self):
        return self.__default_wait_timeout
        
    @default_wait_timeout.setter
    def default_wait_timeout(self, timeout):
        self.__default_wait_timeout = timeout
        
    @property
    def delay_before_run_seconds(self):
        return self.__delay_before_run_sec
        
    def start(self)->None:
        super().start()
        SessionContext.instance().multitask_manager.set_process_id(self.__unique_name, MultitaskManager.get_process_id(process=self))
    
    def run(self)->None:
        SessionContext.instance().multitask_manager.set_process_thread_uid(self.__unique_name, MultitaskManager.get_thread_uid())
        super().run()
    
    def join(self, timeout=undefined_argument, raise_if_still_alive=True):
        """
        See Process.join documentation for default behavior.
        
        This implementation tries to avoid deadlocks by special and default timeout value undefined_argument.
        With any other timeout value, including None, default behavior is happening.
        If timeout argument is undefined_argument, it means that it should stop by itself without deadlock.
        In this case, a timeout value Config.join_timeout_seconds is used.
        
        If argument raise_if_still_alive is True (default) and if process is still alive after join, an exception is raised.
        If timeout is undefined_argument, a TimeoutTechnicalException is raised, else a FunctionalException.
        """
        timeout_str = "long and finite" if timeout is undefined_argument else f"{timeout}s" if timeout else "none"
        logger.debug(f"Joining process '{self.name}' ; timeout={timeout_str} ...")
        
        real_timeout = timeout if timeout is not undefined_argument else Config.join_timeout_seconds
        super().join(real_timeout)
        
        logger.debug(f"End of joining process '{self.name}' ; timeout={timeout_str} ; alive:{self.is_alive()}")
        
        if self.is_alive():
            if raise_if_still_alive:
                if timeout is undefined_argument:
                    raise TimeoutTechnicalException(f"Process '{self.name}' is still alive after join")
                else:
                    raise FunctionalException(f"Process '{self.name}' is still alive after join")
            else:
                logger.error(f"Process '{self.name}' is still alive after join")
    
    def wait_before_run(self):
        if self.delay_before_run_seconds is not None:
            try:
                time.sleep(self.delay_before_run_seconds)
            except Exception as exc:
                logger.exception(f"Exception while waiting delay before run (delay: {self.delay_before_run_seconds} ; type: {Typing.get_object_class_fullname(self.delay_before_run_seconds)})")
                
    # def wait_is_idle(self, timeout=None):
    #     """ Wait event self._is_idle"""
    #     self._wait(self.__is_idle, "is idle", timeout=timeout)
    #
    # def _wait(self, event, event_details, timeout=None):
    #     """ Wait given threading.Event"""
    #     is_set = False
    #     wait_round_counter = 0
    #     round_wait_seconds = 1
    #     if timeout is None:
    #         timeout = self.__default_wait_timeout
    #
    #     logger.debug("[{}] Waiting {}...".format(self.name, event_details))
    #     while not is_set:
    #         wait_round_counter += 1
    #         is_set = event.wait(round_wait_seconds)
    #
    #         if not is_set:
    #             if wait_round_counter * round_wait_seconds * 1000 > timeout:
    #                 raise TimeoutError("[{}] Timeout when waiting {}".format(self.name, event_details))
    #             elif wait_round_counter % 10 == 0:
    #                 logger.debug("[{}] Still waiting {} (round {})".format(self.name, event_details, wait_round_counter))
    #     logger.debug("[{}] Finished waiting {}...".format(self.name, event_details))

class InterruptableProcess(Process):
    """ Helper class managing a process interruptable.
    It gives only the interface, sub-classes must implement if it is really interruptable and how.
    """
    
    def __init__(self, name, default_wait_timeout = None, register_process = True, delay_before_run_sec=None):
        super().__init__(name, default_wait_timeout = default_wait_timeout, register_process = register_process, delay_before_run_sec=delay_before_run_sec)

        # Manage interrupt
        # self.__interrupt_lock = threading.Lock()
        # self.__interrupt_event = threading.Event()
    
    @property    
    def is_interruptable(self):
        # return True
        raise NotImplementedError
    
    @property
    def is_interrupted(self):
        return False
    #     with self.__interrupt_lock:
    #         return self.__interrupt_event.is_set()

    def interrupt(self):
        # if not self.is_interrupted:
        #     logger.debug("Interrupt thread '{}'".format(self.name))
        #     with self.__interrupt_lock:
        #         self.__interrupt_event.set()
        raise NotImplementedError
    
    def _raise_if_interrupted(self):
        if self.is_interrupted:
            raise InterruptedError
        


class ThreadAsProcess(InterruptableProcess):
    """
    WARNING: Do not use, it is under construction
    """
    def __init__(self, thread):
        super().__init__()
        self.__thread = thread
        
    def run(self):
        # Start running by superclass run
        super().run()
        
        return self.__thread.run()
    
    

