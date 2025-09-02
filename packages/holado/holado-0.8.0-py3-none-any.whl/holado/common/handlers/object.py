
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

from builtins import object
import logging
from holado.common.handlers.enums import ObjectStates

logger = None

def initialize_logger():
    global logger
    logger = logging.getLogger(__name__)


class Object(object):
    def __init__(self, name=None):
        self.__name = name
        self.__obj_state = ObjectStates.Created

    @property
    def name(self):
        if self.__name:
            return self.__name
        else:
            return str(self)

    @property
    def object_state(self):
        return self.__obj_state
    
    @object_state.setter
    def object_state(self, state):
        from holado_core.common.tools.tools import Tools
        from holado_python.standard_library.typing import Typing
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"State changed for object '{self.name}' (type: {Typing.get_object_class_fullname(self)}): {self.__obj_state} -> {state}")
        self.__obj_state = state


class DeleteableObject(Object):
    """
    Add to a class deleting features:the possibility to be deleted
        - Self deleting actions
        - Register functions to call on delete
    
    Note: It is highly recommended to set garbage collector periodicity with GcManager.collect_periodically method (see method documentation)
    """
    
    def __init__(self, name=None):
        super().__init__(name)
        
        self.__on_delete_funcs = []
        self.__on_delete_gc_collect = False
        self.__is_deleteable = True
    
    @property
    def _is_deleteable(self):
        return self.__is_deleteable
    
    @_is_deleteable.setter
    def _is_deleteable(self, is_deleteable):
        self.__is_deleteable = is_deleteable
    
    def __del__(self):
        try:
            if not self._is_deleteable:
                return
            if self.object_state in [ObjectStates.Deleting, ObjectStates.Deleted]:
                return
            
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Deleting object of ID {id(self)} and type {type(self)}")
            if logger.isEnabledFor(logging.TRACE):  # @UndefinedVariable
                import traceback
                logger.trace("".join(traceback.format_list(traceback.extract_stack())))
            
            # Notes: 
            #   - Garbage collector default mecanism is incompatible with custom object finalizers (cf GcManager.Method __del__ is called by garbage collector. This call can be done in any thread at any moment.
            #   - When SessionContext is under deletion, delete any object by thread is not possible
            from holado.common.context.session_context import SessionContext
            from holado.common.tools.gc_manager import GcManager
            if GcManager.is_collect_threaded() or isinstance(self, SessionContext.TSessionContext) or not SessionContext.has_instance():
                self.__delete()
            else:
                from holado_multitask.multithreading.functionthreaded import FunctionThreaded
                func = FunctionThreaded(self.__delete, name=f"delete object '{self.name}'", register_thread=False, do_log=False)
                func._is_deleteable = False      # Deactivate deletion mechanism of DeleteableObject to avoid an infinite loop
                func.start()
                func.join(timeout=30, raise_if_still_alive=False)   # timeout of 30s to limit deadlock impact ; raise to False since exceptions are omitted in gc collect context
        except AttributeError as exc:
            if "'NoneType' object has no attribute" in str(exc):
                # Simply return, this exception can appear when system in interrupting
                return
            else:
                raise exc
        except Exception as exc:
            if "Python is likely shutting down" in str(exc):
                # Simply return
                return
            else:
                raise exc
    
    def __delete(self):
        try:
            self.delete_object()
        except Exception as exc:
            if "Python is likely shutting down" in str(exc):
                # Simply return
                return
            else:
                raise exc
        
    @property
    def on_delete_call_gc_collect(self):
        return self.__on_delete_gc_collect
        
    @on_delete_call_gc_collect.setter
    def on_delete_call_gc_collect(self, do_call):
        self.__on_delete_gc_collect = do_call
        
    def on_delete_call_func(self, func):
        self.__on_delete_funcs.append(func)
        
    def delete_object(self):
        from holado_core.common.tools.tools import Tools
        from holado_python.standard_library.typing import Typing
        
        if not self._is_deleteable:
            return
        if self.object_state in [ObjectStates.Deleting, ObjectStates.Deleted]:
            return False
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Deleting object '{self.name}' (type: {Typing.get_object_class_fullname(self)})...")
        self.object_state = ObjectStates.Deleting
        
        # Run on_delete functions
        for func in self.__on_delete_funcs:
            try:
                func()
            except:
                logger.exception(f"[{self.name}] Error while running on delete function '{func}'")
                
        self._delete_object()
        
        # Call garbage collector
        if self.__on_delete_gc_collect:
            from holado.common.tools.gc_manager import GcManager
            GcManager.collect()
        
        self.object_state = ObjectStates.Deleted
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Deleted object '{self.name}' (type: {Typing.get_object_class_fullname(self)})")
        
        return True

    def _delete_object(self):
        """
        Implement this method for specific delete actions
        """
        pass
    
    
    
