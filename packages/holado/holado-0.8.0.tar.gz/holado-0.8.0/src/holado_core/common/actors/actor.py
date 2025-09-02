#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

import logging
import abc
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.actors.actions import Action
from holado_core.common.handlers.redo import Redo
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



class Actor(object):
    """ Base class for actor.
    An actor defines which actions are possible and how to process them.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, module_name):
        self.__module_name = module_name
        self.__actor_by_module_name = {}
        
    def initialize(self):
        """
        Initialize actor
        """
        pass
    
    @property
    def module_name(self):
        return self.__module_name
    
    def _get_actor_for_module(self, name):
        """
        @param name Module name
        @return Module actor
        """
        if name not in self.__actor_by_module_name:
            self.__actor_by_module_name[name] = self._initialize_module(name)
        return self.__actor_by_module_name[name]
    
    def _initialize_module(self, name):
        """
        Initialize a new instance of given module name
        @param name Module name
        @return New module instance
        """
        raise TechnicalException(f"Unmanaged module '{name}'")
    
    def _call_action_from_module(self, finder_info, method_name, *args, **kwargs):
        if finder_info is not None and finder_info.module_name is not None:
            module = self._get_actor_for_module(finder_info.module_name)
            if hasattr(module, method_name):
                method = getattr(module, method_name)
            else:
                raise TechnicalException(f"Method '{method_name}' is missing in module '{finder_info.module_name}'")
            return method(*args, **kwargs)
        else:
            raise TechnicalException("No such action")

    def act_then(self, action_1, action_2):
        """
        @param action_1 First action
        @param action_2 Second action
        @return Action that process first action then second action
        """
        def func(*args, **kwargs):
            result_action_1 = action_1.execute(*args, **kwargs)
            return action_2.execute(result_action_1)
        return Action(f"{action_1.name} then {action_2.name}", func)
    
    def _act_with_redo(self, action):
        """
        Manage redo for given action
        @param action Action
        @return New action managing redo
        """
        raise TechnicalException(f"Unmanaged action type '{Typing.get_object_class_fullname(action)}'")
    
    def _get_redo(self, action, *args, **kwargs):
        """
        Redo an action
        @param action Action
        """
        class ActionRedo(Redo):
            def __init__(self):
                super().__init__(f"redo {action.name}")
                
            def _process(self):
                return action.execute(*args, **kwargs)
            
            def _get_waited_description(self):
                return action.name
            
        return ActionRedo()
    
    def redo_until(self, action, action_args, action_kwargs, value, timeout_seconds):
        """
        Redo until action result for given arguments is given value
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param value Value
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_until(value)
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} until '{value}'", func)
    
    def redo_until_none(self, action, action_args, action_kwargs, timeout_seconds):
        """
        Redo until action result for given arguments is None
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_until_none()
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} until None", func)
    
    def redo_until_not_none(self, action, action_args, action_kwargs, timeout_seconds):
        """
        Redo until action result for given arguments is not None
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_until_not_none()
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} until not None", func)
    
    def redo_while(self, action, action_args, action_kwargs, value, timeout_seconds):
        """
        Redo while action result for given arguments is given value
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param value Value
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_while(value)
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} while '{value}'", func)
    
    def redo_while_none(self, action, action_args, action_kwargs, timeout_seconds):
        """
        Redo while action result for given arguments is None
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_while_none()
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} while None", func)
    
    def redo_while_not_none(self, action, action_args, action_kwargs, timeout_seconds):
        """
        Redo while action result for given arguments is not None
        @param action Action
        @param action_args Action args
        @param action_kwargs Action kwargs
        @param timeout_seconds Timeout in seconds (if None, default timeout is used)
        @return New action processing redo
        """
        def func():
            redo = self._get_redo(action, *action_args, **action_kwargs)
            redo.redo_while_not_none()
            if timeout_seconds is not None:
                redo.with_timeout(timeout_seconds)
            redo.execute()
            return None
            
        return Action(f"redo {action.name} while not None", func)
    
    
    
    