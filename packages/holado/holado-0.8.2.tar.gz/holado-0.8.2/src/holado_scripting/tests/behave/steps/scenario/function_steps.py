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
from holado_core.common.block.scope_steps import ScopeSteps
from holado_core.common.tools.tools import Tools

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



#################################################
##  Steps to define functions

@Given(r"define function (?P<function_name>{Str}):", accept_scope_in_define=False)
def step_impl(context, function_name):
    if __get_block_manager().is_in_define:
        __get_block_manager().increase_define_level()
    else:
        scope_name = StepTools.evaluate_string_parameter(function_name)
    
        if __get_block_manager().has_scope(scope_name):
            if Tools.do_log(logger, logging.DEBUG):
                logger.debug(f"Redefining scope '{scope_name}'")
            __get_block_manager().delete_scope(scope_name)
        __begin_define_scope_steps(scope_name)

def __begin_define_scope_steps(scope_name):
    lambda_scope_type = lambda ID, name: ScopeSteps(ID=ID, name=name)
    __get_block_manager().begin_define_scope("function", scope_name, lambda_scope_type)

@Given(r'end function', accept_scope_in_define=False)
def step_impl(context):
    if __get_block_manager().is_in_sub_define:
        __get_block_manager().decrease_define_level()
    else:
        __get_block_manager().end_define_scope("function")

@Step(r"call function (?P<function_name>{Str})")
def step_impl(context, function_name):
    scope_name = StepTools.evaluate_string_parameter(function_name)
    __get_block_manager().process_scope(scope_name)


