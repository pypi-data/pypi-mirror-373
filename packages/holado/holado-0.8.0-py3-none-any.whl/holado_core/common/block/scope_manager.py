
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
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class ScopeManager(object):
    '''
    Manage scopes.
    '''
    
    def __init__(self):
        self.__scope_info_by_thread_and_type = {}
    
    
    # Manage scope info
    
    def scope_info(self, scope_type, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        self.__ensure_scope_info_exists(scope_type, thread_id)
        return self.__scope_info_by_thread_and_type[thread_id][scope_type]
    
    def __check_scope_info_exists(self, scope_type, thread_id, raise_exception=True):
        res = thread_id in self.__scope_info_by_thread_and_type and scope_type in self.__scope_info_by_thread_and_type[thread_id]
        if not res and raise_exception:
            raise FunctionalException(f"Scope info doesn't exist (thread: {thread_id} ; scope type: {scope_type})")
        return res
    
    def __ensure_scope_info_exists(self, scope_type, thread_id):
        if thread_id not in self.__scope_info_by_thread_and_type:
            self.__scope_info_by_thread_and_type[thread_id] = {}
        if scope_type not in self.__scope_info_by_thread_and_type[thread_id]:
            self.__scope_info_by_thread_and_type[thread_id][scope_type] = {}
    
    
    # Manage scope levels
    
    def has_scope_level(self, scope_type, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        return self.__check_scope_level_exists(scope_type, thread_id, raise_exception=False)
    
    def scope_level(self, scope_type, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        self.__ensure_scope_level_exists(scope_type, thread_id)
        return self.scope_info(scope_type, thread_id)["level"]
    
    def __check_scope_level_exists(self, scope_type, thread_id, raise_exception=True):
        res = self.__check_scope_info_exists(scope_type, thread_id, raise_exception) and "level" in self.scope_info(scope_type, thread_id)
        if not res and raise_exception:
            raise FunctionalException(f"Scope level doesn't exist (thread: {thread_id} ; scope type: {scope_type})")
        return res
    
    def __ensure_scope_level_exists(self, scope_type, thread_id):
        self.__ensure_scope_info_exists(scope_type, thread_id)
        if "level" not in self.__scope_info_by_thread_and_type[thread_id][scope_type]:
            self.__scope_info_by_thread_and_type[thread_id][scope_type]["level"] = 0
        
    def reset_scope_level(self, scope_type=None, level=0, thread_id=None):
        """
        Reset a scope level to given level.
        If scope_type is None, all scope types of the thread are reset.
        """
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
            
        if scope_type is None:
            if thread_id in self.__scope_info_by_thread_and_type:
                for s_type in self.__scope_info_by_thread_and_type[thread_id]:
                    self.reset_scope_level(s_type, level, thread_id)
        else:
            if self.scope_level(scope_type, thread_id) != level:
                self.__scope_info_by_thread_and_type[thread_id][scope_type]["level"] = level
                if Tools.do_log(logger, logging.DEBUG):
                    logger.debug(f"Scope level reset to {level} (thread: {thread_id} ; scope type: {scope_type})")

    def increase_scope_level(self, scope_type, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        self.__ensure_scope_level_exists(scope_type, thread_id)
        
        self.__scope_info_by_thread_and_type[thread_id][scope_type]["level"] += 1
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Scope level increased to {self.__scope_info_by_thread_and_type[thread_id][scope_type]['level']} (thread {thread_id} ; scope type: {scope_type})")

    def decrease_scope_level(self, scope_type, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        self.__ensure_scope_level_exists(scope_type, thread_id)
        
        self.__scope_info_by_thread_and_type[thread_id][scope_type]["level"] -= 1
        if self.__scope_info_by_thread_and_type[thread_id][scope_type]["level"] < 0:
            raise TechnicalException(f"Scope level decreased under 0 (thread {thread_id} ; scope type: {scope_type})")
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Scope level decreased to {self.__scope_info_by_thread_and_type[thread_id][scope_type]['level']} (thread {thread_id} ; scope type: {scope_type})")
    
    
    # Manage conditions scopes
    
    def log_conditions_info(self, prefix_message, thread_id=None):
        scope_info = self.scope_info("conditions", thread_id)
        if not prefix_message.endswith("."):
            prefix_message += "."
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"{prefix_message} Conditions info: {scope_info}")
    
    def increase_condition_level(self, thread_id=None):
        self.increase_scope_level("conditions", thread_id)
        
        scope_info = self.scope_info("conditions", thread_id)
        if "levels_data" not in scope_info:
            scope_info["levels_data"] = []
        if len(scope_info["levels_data"]) != scope_info["level"] - 1:
            raise TechnicalException(f"levels_data has size {len(scope_info['levels_data'])} whereas level is {scope_info['level']}")
        scope_info["levels_data"].append({"is_valid":False, "had_valid":False})
        
        self.log_conditions_info("Increased condition level")
    
    def decrease_condition_level(self, thread_id=None):
        self.decrease_scope_level("conditions", thread_id)
        
        scope_info = self.scope_info("conditions", thread_id)
        if len(scope_info["levels_data"]) != scope_info["level"] + 1:
            raise TechnicalException(f"levels_data has size {len(scope_info['levels_data'])} whereas level is {scope_info['level']}")
        scope_info["levels_data"].pop()
        
        self.log_conditions_info("Decreased condition level")
        
    def is_in_condition(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        return self.__check_scope_level_exists("conditions", thread_id, raise_exception=False) \
            and self.scope_level("conditions", thread_id) > 0
        
    def is_in_valid_condition(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        res = False
        if self.is_in_condition(thread_id):
            scope_info = self.scope_info("conditions", thread_id)
            res = scope_info["levels_data"][-1]["is_valid"]
        return res
        
    def had_valid_condition(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        res = False
        if self.is_in_condition(thread_id):
            scope_info = self.scope_info("conditions", thread_id)
            res = scope_info["levels_data"][-1]["had_valid"]
        return res
        
    def enter_in_valid_condition(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        if not self.is_in_condition(thread_id):
            raise TechnicalException(f"Not in a condition (conditions info: {self.scope_info('conditions', thread_id)})")
        
        scope_info = self.scope_info("conditions", thread_id)
        scope_info["levels_data"][-1]["is_valid"] = True
        
    def leave_condition(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        if not self.is_in_condition(thread_id):
            raise TechnicalException(f"Not in a condition (conditions info: {self.scope_info('conditions', thread_id)})")
        
        scope_info = self.scope_info("conditions", thread_id)
        if scope_info["levels_data"][-1]["is_valid"]:
            scope_info["levels_data"][-1]["is_valid"] = False
            scope_info["levels_data"][-1]["had_valid"] = True


    # Manage steps scope
    
    def set_step_context(self, step_context, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        
        scope_info = self.scope_info("steps")
        if "levels_data" not in scope_info:
            scope_info["levels_data"] = []

        step_level = self.scope_level("steps")
        if step_level + 1 < len(scope_info["levels_data"]):
            scope_info["levels_data"] = scope_info["levels_data"][0:step_level+1]
        for level in range(step_level+1):
            if level + 1 > len(scope_info["levels_data"]):
                scope_info["levels_data"].append({})
                
        scope_info["levels_data"][step_level]["step_context"] = step_context

    def get_step_context(self, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        
        scope_info = self.scope_info("steps")
        if "levels_data" not in scope_info:
            raise TechnicalException(f"No step level is registered")

        step_level = self.scope_level("steps")
        if step_level >= len(scope_info["levels_data"]):
            raise TechnicalException(f"Step level {step_level} is not registered")
        if "step_context" not in scope_info["levels_data"][step_level]:
            raise TechnicalException(f"No step context is registered for level {step_level}")
            
        return scope_info["levels_data"][step_level]["step_context"]

