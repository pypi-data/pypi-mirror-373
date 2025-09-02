
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
import holado_multitask.multithreading as hmm
from holado.common.handlers.undefined import default_context, undefined_argument
from holado_multitask.multitasking.multitask_manager import MultitaskManager

logger = logging.getLogger(__name__)


class ThreadsManager(object):
    """
    Manage threads run by HolAdo, so that each thread can use HolAdo services.
    """
    
    __has_native_id = hasattr(threading, '_HAVE_THREAD_NATIVE_ID') and threading._HAVE_THREAD_NATIVE_ID  # @UndefinedVariable
    
    @classmethod
    def has_native_id(cls):
        return cls.__has_native_id
    
    def __init__(self, multitask_manager):
        self.__multitask_manager = multitask_manager
        self.__managed_threads_lock = threading.Lock()
        self.__managed_threads_by_scope = {}
    
    def __get_scope_name(self, scope, create_if_doesnt_exist=True):
        res = MultitaskManager.get_scope_name(scope)
        
        if create_if_doesnt_exist:
            with self.__managed_threads_lock:
                if res not in self.__managed_threads_by_scope:
                    self.__managed_threads_by_scope[res] = {}
        
        return res
    
    def register_thread(self, name, thread, scope=default_context):
        scope_name = self.__get_scope_name(scope)
        with self.__managed_threads_lock:
            if name in self.__managed_threads_by_scope[scope_name]:
                # logger.error(f"A thread with name '{name}' is already registered, it will be overwritten: {self.__managed_threads_by_scope[name]}")
                logger.error(f"A thread with name '{name}' is already registered in scope '{scope_name}', it will be overwritten: {self.__managed_threads_by_scope[scope_name][name]}", stack_info=True)
            else:
                logger.debug(f"Registered thread with name '{name}' in scope '{scope_name}': {thread}")
            self.__managed_threads_by_scope[scope_name][name] = thread
        return scope_name

    def unregister_thread(self, name, scope=default_context):
        scope_name = self.__get_scope_name(scope)
        with self.__managed_threads_lock:
            if name in self.__managed_threads_by_scope[scope_name]:
                if self.__managed_threads_by_scope[scope_name][name].is_alive():
                    logger.warn(f"Unregistering thread with name '{name}' from scope '{scope_name}' whereas it is still alive")
                else:
                    logger.debug(f"Unregistered thread with name '{name}' from scope '{scope_name}'")
                del self.__managed_threads_by_scope[scope_name][name]
            else:
                raise Exception(f"Not registered thread of name '{name}' in scope '{scope_name}'")
        return scope_name

    def get_thread(self, name, scope=default_context):
        scope_name = self.__get_scope_name(scope)
        with self.__managed_threads_lock:
            if name in self.__managed_threads_by_scope[scope_name]:
                return self.__managed_threads_by_scope[scope_name][name]
            else:
                raise Exception(f"Not registered thread of name '{name}' in scope '{scope_name}'")

    def interrupt_thread(self, name, scope=default_context, with_join=True, join_timeout=undefined_argument, raise_if_not_interruptable=True):
        interrupt_status, join_status = False, False
        
        thread = self.get_thread(name, scope=scope)
        if thread.is_alive():
            if self.is_interruptable(thread=thread):
                try:
                    thread.interrupt()
                except Exception as exc:
                    # logger.exception("Failed to interrupt thread of name '{}'".format(name))
                    raise exc
                else:
                    interrupt_status = True
                
                if with_join:
                    join_status = thread.join(join_timeout)
            elif raise_if_not_interruptable:
                raise TechnicalException("Thread '{}' is not interruptable".format(name))
        
        return interrupt_status, join_status
        
    def join_thread(self, name, scope=default_context, timeout=undefined_argument):
        thread = self.get_thread(name, scope=scope)
        if thread.is_alive():
            thread.join(timeout=timeout)

    def interrupt_all_threads(self, scope=default_context, with_join=True, join_timeout=undefined_argument):
        """Interrupt all threads that are interruptable."""
        names = self.get_thread_names(scope=scope)
        logger.debug(f"Interrupting all threads in scope '{self.__get_scope_name(scope)}': {names}")
        interrupted_names = []
        for name in names:
            try:
                interrupt_status, _ = self.interrupt_thread(name, scope=scope, with_join=False, raise_if_not_interruptable=False)
            except Exception:
                logger.exception("Failed to interrupt thread of name '{}'".format(name))
            else:
                if interrupt_status:
                    interrupted_names.append(name)
        
        if with_join:
            self.__join_threads(interrupted_names, scope=scope, timeout=join_timeout, skip_not_interruptable=True)

    def join_all_threads(self, scope=default_context, timeout=undefined_argument, skip_not_interruptable=False):
        names = self.get_thread_names(scope=scope)
        self.__join_threads(names, scope=scope, timeout=timeout, skip_not_interruptable=skip_not_interruptable)

    def __join_threads(self, thread_names, scope=default_context, timeout=undefined_argument, skip_not_interruptable=False):
        for name in thread_names:
            if skip_not_interruptable and not self.is_interruptable(name=name, scope=scope):
                continue
            self.join_thread(name, scope=scope, timeout=timeout)
    
    def unregister_all_threads(self, scope=default_context, keep_alive=True):
        names = self.get_thread_names(scope=scope)
        for name in names:
            thread = self.get_thread(name, scope=scope)
            if not keep_alive or keep_alive and not thread.is_alive():
                self.unregister_thread(name, scope=scope)
    
    def get_thread_names(self, scope=default_context):
        scope_name = self.__get_scope_name(scope)
        with self.__managed_threads_lock:
            return sorted(list( self.__managed_threads_by_scope[scope_name].keys() ))
    
    def get_alive_thread_names(self, scope=default_context):
        scope_name = self.__get_scope_name(scope)
        with self.__managed_threads_lock:
            res = sorted(list( self.__managed_threads_by_scope[scope_name].keys() ))
            res = [name for name in res if self.__managed_threads_by_scope[scope_name][name].is_alive()]
            
    def is_interruptable(self, thread=None, name=None, scope=default_context):
        if name is not None:
            thread = self.get_thread(name, scope=scope)
        if thread is None:
            raise TechnicalException("At least one argument must be not None")
        
        return isinstance(thread, hmm.thread.InterruptableThread) and thread.is_interruptable
    
    
    