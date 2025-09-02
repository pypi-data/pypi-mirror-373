
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
import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
import holado_multitask.multiprocessing as hmm
from holado.common.handlers.undefined import undefined_argument

logger = logging.getLogger(__name__)


class ProcessesManager(object):
    """
    Helper class to manage running processes.
    """
    
    
    def __init__(self, multitask_manager):
        self.__multitask_manager = multitask_manager
        self.__managed_processes_lock = threading.Lock()
        self.__managed_processes = {}
    
    def register_process(self, name, process):
        with self.__managed_processes_lock:
            if name in self.__managed_processes:
                logger.error(f"A process with name '{name}' is already registered, it will be overwritten: {self.__managed_processes[name]}")
            else:
                logger.debug(f"Registered process with name '{name}': {process}")
            self.__managed_processes[name] = process
    
    def unregister_process(self, name):
        with self.__managed_processes_lock:
            if name in self.__managed_processes:
                if self.__managed_processes[name].is_alive():
                    logger.warn(f"Unregistering process with name '{name}' whereas it is still alive")
                else:
                    logger.debug(f"Unregistered process with name '{name}'")
                del self.__managed_processes[name]
            else:
                raise Exception("Not registered process of name '{}'".format(name))


    def get_process(self, name):
        with self.__managed_processes_lock:
            if name in self.__managed_processes:
                return self.__managed_processes[name]
            else:
                raise Exception("Unregistered process of name '{}'".format(name))


    def interrupt_process(self, name, with_join=True, join_timeout=undefined_argument, raise_if_not_interruptable=True):
        process = self.get_process(name)
        if process.is_alive():
            if self.is_interruptable(process=process):
                try:
                    process.interrupt()
                except Exception as exc:
                    # logger.exception("Failed to interrupt process of name '{}'".format(name))
                    raise exc
                
                if with_join:
                    process.join(join_timeout)
            elif raise_if_not_interruptable:
                raise TechnicalException("Thread '{}' is not interruptable".format(name))
                


    def join_process(self, name, timeout=undefined_argument):
        process = self.get_process(name)
        if process.is_alive():
            process.join(timeout)


    def interrupt_all_processes(self, with_join=True, join_timeout=undefined_argument):
        """Interrupt all processes that are interruptable."""
        names = self.get_process_names()
        for name in names:
            try:
                if self.is_interruptable(name=name):
                    self.interrupt_process(name, with_join=False)
            except Exception:
                logger.exception("Failed to interrupt process of name '{}'".format(name))

        if with_join:
            self.join_all_processes(timeout=join_timeout, skip_not_interruptable=True)


    def join_all_processes(self, timeout=undefined_argument, skip_not_interruptable=False):
        names = self.get_process_names()
        for name in names:
            if skip_not_interruptable and self.is_interruptable(name=name):
                continue
            self.join_process(name, timeout=timeout)
    

    def unregister_all_processes(self, keep_alive=True):
        names = self.get_process_names()
        for name in names:
            process = self.get_process(name)
            if not keep_alive or keep_alive and not process.is_alive():
                self.unregister_process(name)
    

    def get_process_names(self):
        with self.__managed_processes_lock:
            return sorted(list( self.__managed_processes.keys() ))
    

    def get_alive_process_names(self):
        with self.__managed_processes_lock:
            res = sorted(list( self.__managed_processes.keys() ))
            res = [name for name in res if self.__managed_processes[name].is_alive()]
            

    def is_interruptable(self, process=None, name=None):
        if name is not None:
            process = self.get_process(name)
        if process is None:
            raise TechnicalException("At least one argument must be not None")    
        
        return isinstance(process, hmm.process.InterruptableProcess) and process.is_interruptable
    