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


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.exceptions.technical_exception import TechnicalException
import logging
import copy
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)



def __get_scenario_context():
    return SessionContext.instance().get_scenario_context()

def __get_text_interpreter():
    return __get_scenario_context().get_text_interpreter()

def __get_unique_value_manager():
    return SessionContext.instance().unique_value_manager

def __get_variable_manager():
    return __get_scenario_context().get_variable_manager()



# @Step(r"(?P<var_name>{Variable}) = (?P<value>{AnyStr}|{Int}|{Float}|{List}|{Dict}|\$\{{.+\}}.*|[^' ]*'[^']*'[^ ]*)")
@Step(r"(?P<var_name>{Variable}) = (?P<value>{AnyStr}|{Bytes}|{Int}|{Float}|{List}|{Dict}|\$\{{.+\}}.*)")
def step_impl(context, var_name, value):  # @DuplicatedSignature
    var_name = StepTools.evaluate_variable_name(var_name)
    val = StepTools.evaluate_scenario_parameter(value)
    __get_variable_manager().set_value(var_name, val)


@Given(r"(?P<var_name>{Variable}) = size of (?P<value>{Str})")
def step_impl(context, var_name, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    res = None
    
    # Try "len" method
    try:
        res = len(val)
    except Exception:
        pass
    
    # Try "size" method
    if res is None:
        try:
            res = val.size()
        except Exception:
            pass
    
    if res is None:
        raise TechnicalException(f"Unable to identify size of [{val}] (type: {Typing.get_object_class_fullname(val)})")
    
    __get_variable_manager().register_variable(var_name, res)


@Given(r"(?P<var_name>{Variable}) = list of (?P<value_expression>{Any}) for (?P<iter_var_name>{Variable}) in (?P<iterable_str>{Variable})")
def step_impl(context, var_name, value_expression, iter_var_name, iterable_str):  # @DuplicatedSignature
    res = []
    iterable = StepTools.evaluate_scenario_parameter(iterable_str)
    for x in iterable:
        __get_variable_manager().register_variable(iter_var_name, x, log_level=logging.TRACE)  # @UndefinedVariable
        res.append(StepTools.evaluate_scenario_parameter(value_expression))
    __get_variable_manager().register_variable(var_name, res)


@Given(r"(?P<var_name>{Variable}) = sorted (?P<value>{Variable})")
def step_impl(context, var_name, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    res = sorted(val)
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = sorted (?P<value>{Variable}) by (?P<lambda_var_name>{Variable}):(?P<lambda_expression>{Any})")
def step_impl(context, var_name, value, lambda_var_name, lambda_expression):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    res = sorted(val, key=eval(f"lambda {lambda_var_name}: {lambda_expression}"))
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = copy of (?P<value>{Variable})")
def step_impl(context, var_name, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    res = copy.copy(val)
    __get_variable_manager().register_variable(var_name, res)

@Given(r"(?P<var_name>{Variable}) = deep copy of (?P<value>{Variable})")
def step_impl(context, var_name, value):  # @DuplicatedSignature
    val = StepTools.evaluate_scenario_parameter(value)
    res = copy.deepcopy(val)
    __get_variable_manager().register_variable(var_name, res)


