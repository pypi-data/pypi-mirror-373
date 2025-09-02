
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
from holado_scripting.text.interpreter.text_interpreter import TextInterpreter
from holado_scripting.common.tools.dynamic_text_manager import DynamicTextManager
from holado_scripting.common.tools.variable_manager import VariableManager
from holado.common.context.context import Context
import logging
from holado_scripting.common.tools.expression_evaluator import ExpressionEvaluator
from holado.common.context.session_context import SessionContext
from holado_core.common.block.scope_manager import ScopeManager
from holado_core.common.block.block_manager import BlockManager
from datetime import datetime
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.text.verifier.text_verifier import TextVerifier
from holado_multitask.multitasking.multitask_manager import MultitaskManager

logger = logging.getLogger(__name__)


class ScenarioContext(Context):
    def __init__(self, scenario):
        super().__init__("Scenario", with_post_process=True)
        
        self.__scenario = scenario
        
        self.__start_date = datetime.now()
        self.__end_date = None
        
        self.__main_thread_uid = SessionContext.instance().multitask_manager.main_thread_uid
        self.__steps_by_thread_uid = {}
        
    def __str__(self):
        return f"{{ScenarioContext({id(self)}):{self.scenario.name}}}"

    @property
    def scenario(self):
        return self.__scenario
    
    @property
    def start_datetime(self):
        return self.__start_date
    
    @property
    def end_datetime(self):
        return self.__end_date
    
    @property
    def duration(self):
        if self.__end_date is not None:
            return (self.__end_date - self.__start_date).total_seconds()
        else:
            return None
    
    def has_step(self, thread_uid=None):
        if thread_uid is None:
            thread_uid = MultitaskManager.get_thread_uid()
        return thread_uid in self.__steps_by_thread_uid and len(self.__steps_by_thread_uid[thread_uid]) > 0
    
    def get_current_step(self, thread_uid=None):
        return self.get_step(-1, thread_uid=thread_uid)
    
    def add_step(self, step_context, thread_uid=None):
        if thread_uid is None:
            thread_uid = MultitaskManager.get_thread_uid()
        if thread_uid not in self.__steps_by_thread_uid:
            self.__steps_by_thread_uid[thread_uid] = []
        self.__steps_by_thread_uid[thread_uid].append(step_context)
    
    def get_step(self, index, thread_uid=None):
        if thread_uid is None:
            thread_uid = MultitaskManager.get_thread_uid()
        if not self.has_step(thread_uid):
            raise TechnicalException(f"Scenario has no step (for thread UID '{thread_uid}'")
        return self.__steps_by_thread_uid[thread_uid][index]
    
    @property
    def block_manager(self):
        if not self.has_object("block_manager"):
            self.set_object("block_manager", BlockManager())
        return self.get_object("block_manager")
    
    @property
    def scope_manager(self):
        if not self.has_object("scope_manager"):
            self.set_object("scope_manager", ScopeManager())
        return self.get_object("scope_manager")


    def has_dynamic_text_manager(self):
        return self.has_object("dynamic_text_manager")
        
    def get_dynamic_text_manager(self) -> DynamicTextManager:
        if not self.has_dynamic_text_manager():
            dynamic_text_manager = DynamicTextManager("scenario")
            self.set_object("dynamic_text_manager", dynamic_text_manager)
            dynamic_text_manager.initialize(SessionContext.instance().unique_value_manager)
        return self.get_object("dynamic_text_manager")
        
    def has_text_interpreter(self):
        return self.has_object("text_interpreter")
        
    def get_text_interpreter(self):
        if not self.has_text_interpreter():
            interpreter = TextInterpreter()
            self.set_object("text_interpreter", interpreter)
            interpreter.initialize(self.get_variable_manager(), self.get_expression_evaluator(), self.get_text_verifier(), self.get_dynamic_text_manager())
        return self.get_object("text_interpreter")
        
    def has_text_verifier(self):
        return self.has_object("text_verifier")
        
    def get_text_verifier(self):
        if not self.has_text_verifier():
            verifier = TextVerifier()
            self.set_object("text_verifier", verifier)
            verifier.initialize(self.get_variable_manager(), self.get_expression_evaluator(), self.get_text_interpreter())
        return self.get_object("text_verifier")
        
    def has_variable_manager(self):
        return self.has_object("variable_manager")
        
    def get_variable_manager(self) -> VariableManager:
        if not self.has_variable_manager():
            manager = VariableManager(SessionContext.instance().get_feature_context().get_variable_manager())
            self.set_object("variable_manager", manager)
            manager.initialize(self.get_dynamic_text_manager(), SessionContext.instance().unique_value_manager)
        return self.get_object("variable_manager")
    
    def has_expression_evaluator(self):
        return self.has_object("expression_evaluator")
    
    def get_expression_evaluator(self) -> ExpressionEvaluator:
        if not self.has_expression_evaluator():
            evaluator = ExpressionEvaluator()
            self.set_object("expression_evaluator", evaluator)
            uvm = SessionContext.instance().unique_value_manager
            evaluator.initialize(self.get_dynamic_text_manager(), uvm, self.get_text_interpreter(), self.get_variable_manager())
        return self.get_object("expression_evaluator")
    
    def end(self):
        self.__end_date = datetime.now()


        