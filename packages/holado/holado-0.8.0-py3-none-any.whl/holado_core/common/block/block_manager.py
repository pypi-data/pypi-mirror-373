
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
from typing import NamedTuple
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_core.common.block.scope_function import ScopeFunction
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class BlockManager(object):
    '''
    Manage blocks.
    
    Currently it manages definition of scopes (functions and loops).
    '''
    
    def __init__(self):
        self.__scope_by_id = {}
        self.__scope_define_by_thread = {}
        
    @property
    def is_in_define(self):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        thread_id = MultitaskManager.get_thread_id()
        return thread_id in self.__scope_define_by_thread
    
    @property
    def is_in_sub_define(self):
        return self.__get_scope_define().level > 1
    
    @property
    def scope_in_define(self):
        if not self.is_in_define:
            raise FunctionalException("No block is under define")
        scope_id = self.__get_scope_define().scope_id
        return self.__scope_by_id[scope_id]
    
    def begin_define_scope(self, scope_type, scope_name, block_scope_type=None):
        """
        Begin define of a scope of given scope_name.
        Parameter block_scope_type specifies the scope class to use (any class inheriting from BaseScope ; default: ScopeFunction).
        """
        if block_scope_type is None:
            block_scope_type = ScopeFunction
            
        if self.is_in_define:
            raise FunctionalException("A block is already under define")

        scope_id = self.__get_scope_ID(scope_name)
        if scope_id in self.__scope_by_id:
            raise FunctionalException(f"Scope '{scope_name}' (ID: {scope_id}) was already defined")
        
        block_scope = block_scope_type(ID=scope_id, name=scope_name)
        
        self.__new_scope_define(scope_type, scope_id, scope_name)
        self.__scope_by_id[scope_id] = block_scope
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[BlockManager] Define of '{scope_name}' (ID: {scope_id}) => begin")
        
    def end_define_scope(self, scope_type):
        if not self.is_in_define:
            raise TechnicalException("No block is under define")
        
        scope_define = self.__get_scope_define()
        if scope_define.scope_type != scope_type:
            raise TechnicalException(f"Scope under define is '{scope_define.scope_type}' (expected: '{scope_type}')")
        
        self.__delete_scope_define(scope_define.scope_id)
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"[BlockManager] Define of '{scope_define.scope_name}' (ID: {scope_define.scope_id}) => end")

    def increase_define_level(self):
        self.__get_scope_define().level += 1

    def decrease_define_level(self):
        self.__get_scope_define().level -= 1
        
    def has_scope(self, scope_name):
        scope_id = self.__get_scope_ID(scope_name)
        return scope_id in self.__scope_by_id

    def delete_scope(self, scope_name=None, scope_id=None):
        if scope_id is None:
            scope_id = self.__get_scope_ID(scope_name)
        
        # Check scope
        self.__check_block_is_not_under_define(scope_id)
        self.__check_block_is_defined(scope_id)
        
        # Delete scope
        del self.__scope_by_id[scope_id]

    def __check_block_is_not_under_define(self, block_id):
        scope_define = self.__get_scope_define(raise_exception=False)
        if scope_define is not None and scope_define.scope_id == block_id:
            raise FunctionalException(f"Block '{self.scope_in_define.name}' is under define")

    def __check_block_is_defined(self, block_id):
        if block_id not in self.__scope_by_id:
            raise FunctionalException(f"Block of ID '{block_id}' is not define")

    def __get_scope_ID(self, scope_name):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        return f"SCOPE[{MultitaskManager.get_thread_id()};{scope_name}]"
    
    def __get_scope_define(self, thread_id=None, raise_exception=True):
        from holado_multitask.multitasking.multitask_manager import MultitaskManager
        if thread_id is None:
            thread_id = MultitaskManager.get_thread_id()
        if thread_id not in self.__scope_define_by_thread:
            if raise_exception:
                raise TechnicalException(f"No scope is under define for thread {thread_id}")
            else:
                return None
        return self.__scope_define_by_thread[thread_id]

    def __new_scope_define(self, scope_type, scope_id, scope_name, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()

        res = NamedTuple("ScopeDefine", scope_type=str, scope_id=str, scope_name=str, level=int)
        res.scope_type = scope_type
        res.scope_id = scope_id
        res.scope_name = scope_name
        res.level = 1
        
        self.__scope_define_by_thread[thread_id] = res
        return res

    def __delete_scope_define(self, scope_id, thread_id=None):
        if thread_id is None:
            from holado_multitask.multitasking.multitask_manager import MultitaskManager
            thread_id = MultitaskManager.get_thread_id()
        if self.__get_scope_define(thread_id).scope_id != scope_id:
            raise TechnicalException(f"For thread {thread_id}, scope under define has ID '{self.__get_scope_define(thread_id).scope_id}' (expected: {scope_id})")
        del self.__scope_define_by_thread[thread_id]
    
    def process_scope(self, scope_name=None, scope_id=None, *args, **kwargs):
        res = None
        if scope_id is None:
            scope_id = self.__get_scope_ID(scope_name)
        
        # Check scope
        self.__check_block_is_not_under_define(scope_id)
        self.__check_block_is_defined(scope_id)
        
        # Start scope
        func = self.__scope_by_id[scope_id]
        try:
            res = func.process(*args, **kwargs)
        except (FunctionalException, TechnicalException) as exc:
            raise exc
        except Exception as exc:
            raise TechnicalException(exc)
        
        return res

