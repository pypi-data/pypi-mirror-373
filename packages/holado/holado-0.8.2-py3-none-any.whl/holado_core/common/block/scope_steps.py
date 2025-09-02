
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
from holado_core.common.block.base import BaseScope
from holado_core.common.block.block_steps import BlockSteps
from holado_test.behave.behave import execute_steps
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


class ScopeSteps(BaseScope):
    '''
    Scope block that should only contains steps.
    This scope block is used when a new scope (function, for,...) is defined in a scenario.

    When processing this scope, a 'context' is supposed to be passed as parameter to 'process' method
    Warning: it remains possible to add any block, not only steps. Be carefull that added blocks are compatible with parameter 'context' passed to 'process' method.
    '''
    
    def __init__(self, name, ID=None):
        super().__init__(f"steps scope {name}", ID=ID)
        
    def add_steps(self, steps_str):
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"In scope '{self.name}', add steps:\n{steps_str}")
        self.add_block( BlockSteps(steps_str) )
    
class ScopeForSteps(ScopeSteps):
    def __init__(self, name, iter_var_name, iterable, ID=None, variable_manager=None, scope_manager=None):
        super().__init__(name, ID=ID)
        
        self.__iter_var_name = iter_var_name
        self.__iterable = iterable
        
        self.__variable_manager = variable_manager
        self.__scope_manager = scope_manager
    
    def process(self, *args, **kwargs):
        """
        Process the scope.
        Returns last scope step result
        """
        res = None
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Processing scope [{self.name}]: begin")

        self._process_start()
        try:
            for index, value in enumerate(self.__iterable):
                execute_steps(u"""
                    Given FOR_INDEX_{iter_var_name} = {index}
                    """.format(iter_var_name=self.__iter_var_name, index=index))
                self.__variable_manager.register_variable(self.__iter_var_name, value)
                
                if self.__scope_manager:
                    level_already_exists = self.__scope_manager.has_scope_level("steps")
                    origin_level = self.__scope_manager.scope_level("steps")
                    if level_already_exists:
                        self.__scope_manager.increase_scope_level("steps")
                
                try:
                    self._process_blocks(*args, **kwargs)
                finally:
                    if self.__scope_manager:
                        self.__scope_manager.reset_scope_level("steps", origin_level)
        finally:
            self._process_end()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Processing scope [{self.name}]: end")

        return res
    
class ScopeWhileSteps(ScopeSteps):
    def __init__(self, name, condition_expression, ID=None, expression_evaluator=None, scope_manager=None):
        super().__init__(name, ID=ID)
        
        self.__condition_expression = condition_expression
        
        self.__expression_evaluator = expression_evaluator
        self.__scope_manager = scope_manager
    
    def process(self, *args, **kwargs):
        """
        Process the scope.
        Returns last scope step result
        """
        res = None
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"Processing scope [{self.name}]: begin")

        self._process_start()
        try:
            n = 0
            _, cond = self.__expression_evaluator.evaluate_python_expression(self.__condition_expression)
            if not (isinstance(cond, bool) or Converter.is_boolean(cond)):
                raise FunctionalException(f"Condition expression is not a boolean: [{self.__condition_expression}] => [{cond}] (type: {Typing.get_object_class_fullname(cond)})")
            
            while isinstance(cond, bool) and cond or Converter.is_boolean(cond) and Converter.to_boolean(cond):
                n += 1
                execute_steps(u"""
                    Given WHILE_ITERATION = {n}
                    """.format(n=n))
                
                if self.__scope_manager:
                    level_already_exists = self.__scope_manager.has_scope_level("steps")
                    origin_level = self.__scope_manager.scope_level("steps")
                    if level_already_exists:
                        self.__scope_manager.increase_scope_level("steps")
                
                try:
                    self._process_blocks(*args, **kwargs)
                finally:
                    if self.__scope_manager:
                        self.__scope_manager.reset_scope_level("steps", origin_level)
                
                _, cond = self.__expression_evaluator.evaluate_python_expression(self.__condition_expression)
                if not (isinstance(cond, bool) or Converter.is_boolean(cond)):
                    raise FunctionalException(f"Condition expression is not a boolean: [{self.__condition_expression}] => [{cond}] (type: {Typing.get_object_class_fullname(cond)})")
        finally:
            self._process_end()
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Processing scope [{self.name}]: end")

        return res
    
