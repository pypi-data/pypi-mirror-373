# -*- coding: utf-8 -*-

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
from holado.common.context.session_context import SessionContext
from holado_test.scenario.step_tools import StepTools
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.block.scope_steps import ScopeForSteps, ScopeWhileSteps
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)


def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_block_manager():
    return __get_scenario_context().block_manager

def __get_scope_manager():
    return __get_scenario_context().scope_manager

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()

def __get_expression_evaluator():
    return __get_scenario_context().get_expression_evaluator()



###################################################################################################
##  Steps managing loops
###################################################################################################

## /!\ While @For decorator is not working (cf testing_behave/scenario/behave.py), use instead "@Given for" 



#################################################
##  Steps to manage "for" loops

@Given(r"for (?P<iter_var_name>{Variable}) in (?P<iterable_expression>{Any}):", accept_scope_in_define=False)
def step_impl(context, iter_var_name, iterable_expression):
    if __get_block_manager().is_in_define:
        __get_block_manager().increase_define_level()
    else:
        iter_var_name = StepTools.evaluate_variable_name(iter_var_name)
        iterable = StepTools.evaluate_scenario_parameter(iterable_expression)
        scope_name = context.step.name
        
        if __get_block_manager().has_scope(scope_name):
            raise TechnicalException(f"For loop scope '{scope_name}' is already defined")
        __begin_define_scope_for_steps(scope_name, iter_var_name, iterable)

def __begin_define_scope_for_steps(scope_name, iter_var_name, iterable):
    lambda_scope_type = lambda ID, name: ScopeForSteps(ID=ID, name=name, iter_var_name=iter_var_name, iterable=iterable, variable_manager=__get_variable_manager(), scope_manager=__get_scope_manager())
    __get_block_manager().begin_define_scope("for", scope_name, lambda_scope_type)
    
# @For('end')
@Given(r'end for', accept_scope_in_define=False)
def step_impl(context):
    # TODO EKL: add verification that sub define is a 'for'
    if __get_block_manager().is_in_sub_define:
        __get_block_manager().decrease_define_level()
    else:
        block_define = __get_block_manager().scope_in_define
        __get_block_manager().end_define_scope("for")
        __get_block_manager().process_scope(scope_id=block_define.ID)
        __get_block_manager().delete_scope(scope_id=block_define.ID)



#################################################
##  Steps to manage "while" loops

@Given(r'while (?P<condition_expression>{Any}):', accept_scope_in_define=False)
def step_impl(context, condition_expression):
    if __get_block_manager().is_in_define:
        __get_block_manager().increase_define_level()
    else:
        scope_name = context.step.name
        
        if __get_block_manager().has_scope(scope_name):
            raise TechnicalException(f"While loop scope '{scope_name}' is already defined")
        __begin_define_scope_while_steps(scope_name, condition_expression)

def __begin_define_scope_while_steps(scope_name, condition_expression):
    lambda_scope_type = lambda ID, name: ScopeWhileSteps(ID=ID, name=name, condition_expression=condition_expression, expression_evaluator=__get_expression_evaluator(), scope_manager=__get_scope_manager())
    __get_block_manager().begin_define_scope("while", scope_name, lambda_scope_type)
    
@Given(r'end while', accept_scope_in_define=False)
def step_impl(context):
    # TODO EKL: add verification that sub define is a 'while'
    if __get_block_manager().is_in_sub_define:
        __get_block_manager().decrease_define_level()
    else:
        block_define = __get_block_manager().scope_in_define
        __get_block_manager().end_define_scope("while")
        __get_block_manager().process_scope(scope_id=block_define.ID)
        __get_block_manager().delete_scope(scope_id=block_define.ID)





