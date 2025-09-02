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
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.tools.converters.converter import Converter
from holado_python.standard_library.typing import Typing

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
##  Steps to manage "if / else if /else"

@Given(r"if (?P<condition_expression>{Any}):", accept_condition=False)
def step_impl(context, condition_expression):
    __get_scope_manager().log_conditions_info(f"Before evaluation of if condition expression [{condition_expression}]")
    __get_scope_manager().increase_condition_level()
    _, cond = __get_expression_evaluator().evaluate_python_expression(condition_expression)
    if isinstance(cond, bool) or Converter.is_boolean(cond):
        if isinstance(cond, bool) and cond or Converter.is_boolean(cond) and Converter.to_boolean(cond):
            __get_scope_manager().enter_in_valid_condition()
    else:
        raise FunctionalException(f"Condition expression is not a boolean: [{condition_expression}] => [{cond}] (type: {Typing.get_object_class_fullname(cond)})")
    __get_scope_manager().log_conditions_info(f"After evaluation of if condition expression [{condition_expression}]")

@Given(r"else if (?P<condition_expression>{Any}):", accept_condition=False)
def step_impl(context, condition_expression):
    __get_scope_manager().leave_condition()
    if not __get_scope_manager().had_valid_condition():
        _, cond = __get_expression_evaluator().evaluate_python_expression(condition_expression)
        if isinstance(cond, bool) or Converter.is_boolean(cond):
            if isinstance(cond, bool) and cond or Converter.is_boolean(cond) and Converter.to_boolean(cond):
                __get_scope_manager().enter_in_valid_condition()
        else:
            raise FunctionalException(f"Condition expression is not a boolean: [{condition_expression}] => [{cond}] (type: {Typing.get_object_class_fullname(cond)})")
        __get_scope_manager().log_conditions_info(f"After evaluation of elif condition expression [{condition_expression}]")

@Given(r"else:", accept_condition=False)
def step_impl(context):
    __get_scope_manager().leave_condition()
    if not __get_scope_manager().had_valid_condition():
        __get_scope_manager().enter_in_valid_condition()
    __get_scope_manager().log_conditions_info(f"After else")

@Given(r"end if", accept_condition=False)
def step_impl(context):
    # TODO EKL: add verification that sub define is a 'if'
    __get_scope_manager().decrease_condition_level()





